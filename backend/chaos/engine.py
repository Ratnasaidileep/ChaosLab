"""ChaosLab Experiment Orchestration Engine.

Coordinates the complete chaos lifecycle:
Injection -> Active Detection -> Duration Hold -> Recovery -> Verification -> Metrics Recording.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import httpx

from backend.config import settings
from backend import models
from backend.chaos.injectors import inject_failure, get_service_url
from backend.chaos.recovery import execute_recovery_action, verify_service_health

logger = logging.getLogger("chaoslab.engine")


def parse_iso(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def calculate_metrics(
    failure_ts: Optional[str],
    detection_ts: Optional[str],
    recovery_start_ts: Optional[str],
    recovery_ts: Optional[str]
) -> Dict[str, Optional[float]]:
    """Calculates Detection Time, Recovery Duration, and Total Downtime in milliseconds.
    
    Handles missing timestamps correctly without inventing numbers.
    """
    f_dt = parse_iso(failure_ts)
    d_dt = parse_iso(detection_ts)
    rs_dt = parse_iso(recovery_start_ts)
    r_dt = parse_iso(recovery_ts)

    detection_time_ms = None
    if f_dt and d_dt and d_dt >= f_dt:
        detection_time_ms = round((d_dt - f_dt).total_seconds() * 1000, 2)

    recovery_duration_ms = None
    if rs_dt and r_dt and r_dt >= rs_dt:
        recovery_duration_ms = round((r_dt - rs_dt).total_seconds() * 1000, 2)

    total_downtime_ms = None
    if f_dt and r_dt and r_dt >= f_dt:
        total_downtime_ms = round((r_dt - f_dt).total_seconds() * 1000, 2)

    return {
        "detection_time_ms": detection_time_ms,
        "recovery_duration_ms": recovery_duration_ms,
        "total_downtime_ms": total_downtime_ms
    }


class ChaosEngine:
    def __init__(self):
        self.active_experiment: Optional[Dict[str, Any]] = None
        self._cancel_event = asyncio.Event()
        self.service_health_cache: Dict[str, Dict[str, Any]] = {
            "product-service": {
                "id": "product-service",
                "name": "Product Service",
                "url": settings.PRODUCT_SERVICE_URL,
                "status": "HEALTHY",
                "last_checked": datetime.now(timezone.utc).isoformat(),
                "last_failure": None,
                "last_recovery": None,
                "latency_ms": 0.0,
                "details": {}
            },
            "order-service": {
                "id": "order-service",
                "name": "Order Service",
                "url": settings.ORDER_SERVICE_URL,
                "status": "HEALTHY",
                "last_checked": datetime.now(timezone.utc).isoformat(),
                "last_failure": None,
                "last_recovery": None,
                "latency_ms": 0.0,
                "details": {}
            }
        }

    def _log_event(self, exp: Dict[str, Any], message: str, level: str = "INFO"):
        ts = datetime.now(timezone.utc).isoformat()
        exp["logs"].append({"timestamp": ts, "level": level, "message": message})
        logger.info(f"[{exp['id']}] {message}")

    async def probe_is_failed(self, service_url: str) -> bool:
        """Probe service to check if it exhibits failure (503, error, or unresponsiveness)."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(f"{service_url}/health")
                if resp.status_code != 200:
                    return True
                data = resp.json()
                return data.get("status") != "healthy"
        except Exception:
            return True

    async def run_experiment_lifecycle(self, exp: Dict[str, Any]):
        """Runs the asynchronous chaos experiment state machine."""
        exp_id = exp["id"]
        target = exp["target_service"]
        exp_type = exp["type"]
        params = exp["parameters"]
        duration = params.get("duration_seconds", 15)

        self._cancel_event.clear()
        injection_mode = "http_simulation"

        try:
            # Step 1: Inject Failure
            exp["status"] = "INJECTING"
            self._log_event(exp, f"Initiating controlled failure injection: {exp_type} on {target}")
            models.save_experiment(exp)

            injection_res = await inject_failure(exp_id, exp_type, target, params)
            injection_mode = injection_res.get("mode", "http_simulation")
            exp["failure_timestamp"] = datetime.now(timezone.utc).isoformat()
            exp["status"] = "RUNNING"
            self._log_event(exp, f"Failure injected successfully via {injection_mode}")
            models.save_experiment(exp)

            # Step 2: Detect Failure
            detection_start = asyncio.get_event_loop().time()
            detection_timeout = settings.DETECTION_TIMEOUT_SECONDS
            service_url = get_service_url(target)
            detected = False

            while (asyncio.get_event_loop().time() - detection_start) < detection_timeout:
                if self._cancel_event.is_set():
                    break
                detected = await self.probe_is_failed(service_url)
                if detected:
                    exp["detection_timestamp"] = datetime.now(timezone.utc).isoformat()
                    exp["status"] = "DETECTED"
                    metrics = calculate_metrics(
                        exp["failure_timestamp"],
                        exp["detection_timestamp"],
                        None,
                        None
                    )
                    exp["detection_time_ms"] = metrics["detection_time_ms"]
                    self._log_event(exp, f"Failure detected by automated monitor in {exp['detection_time_ms']}ms")
                    models.save_experiment(exp)
                    break

                await asyncio.sleep(0.5)

            if not detected and not self._cancel_event.is_set():
                self._log_event(exp, "Warning: Failure was not detected within timeout window", level="WARNING")

            # Step 3: Hold Failure for specified duration (unless cancelled)
            hold_time = 0.0
            while hold_time < duration and not self._cancel_event.is_set():
                await asyncio.sleep(0.5)
                hold_time += 0.5

            if self._cancel_event.is_set():
                exp["status"] = "CANCELLED"
                exp["recovery_outcome"] = "CANCELLED_BY_USER"
                self._log_event(exp, "Experiment cancelled by operator request", level="WARNING")
                # Immediately execute recovery
                await execute_recovery_action(target, exp_type, injection_mode)
                models.save_experiment(exp)
                return

            # Step 4: Initiate Automatic Recovery
            exp["status"] = "RECOVERING"
            exp["recovery_start_timestamp"] = datetime.now(timezone.utc).isoformat()
            self._log_event(exp, f"Triggering automatic recovery mechanism for {target}")
            models.save_experiment(exp)

            await execute_recovery_action(target, exp_type, injection_mode)

            # Step 5: Verify Health Restoration
            exp["status"] = "VERIFYING"
            self._log_event(exp, f"Verifying service health with active polling (timeout: {settings.RECOVERY_TIMEOUT_SECONDS}s)")
            models.save_experiment(exp)

            verified, health_details = await verify_service_health(
                target,
                timeout_seconds=settings.RECOVERY_TIMEOUT_SECONDS,
                poll_interval=settings.HEALTH_CHECK_INTERVAL_SECONDS
            )

            if verified:
                exp["recovery_timestamp"] = datetime.now(timezone.utc).isoformat()
                exp["status"] = "RECOVERED"
                exp["recovery_outcome"] = "SUCCESS"

                metrics = calculate_metrics(
                    exp["failure_timestamp"],
                    exp["detection_timestamp"],
                    exp["recovery_start_timestamp"],
                    exp["recovery_timestamp"]
                )
                exp["detection_time_ms"] = metrics["detection_time_ms"]
                exp["recovery_duration_ms"] = metrics["recovery_duration_ms"]
                exp["total_downtime_ms"] = metrics["total_downtime_ms"]

                self._log_event(
                    exp,
                    f"Service verified healthy! Recovery Duration: {exp['recovery_duration_ms']}ms, Total Downtime: {exp['total_downtime_ms']}ms"
                )
            else:
                exp["status"] = "FAILED"
                exp["recovery_outcome"] = "FAILED_VERIFICATION_TIMEOUT"
                exp["error_details"] = health_details.get("error", "Service did not pass health check within timeout")
                self._log_event(exp, f"Recovery verification failed: {exp['error_details']}", level="ERROR")

            models.save_experiment(exp)

        except Exception as exc:
            logger.exception(f"Unexpected exception during experiment {exp_id}: {exc}")
            exp["status"] = "FAILED"
            exp["recovery_outcome"] = "ERROR"
            exp["error_details"] = str(exc)
            self._log_event(exp, f"Experiment error: {str(exc)}", level="ERROR")
            # Best-effort recovery attempt on error
            try:
                await execute_recovery_action(target, exp_type, injection_mode)
            except Exception:
                pass
            models.save_experiment(exp)

        finally:
            if self.active_experiment and self.active_experiment["id"] == exp_id:
                self.active_experiment = None

    def start_experiment(
        self,
        exp_type: str,
        target_service: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and dispatch a new chaos experiment."""
        if self.active_experiment is not None:
            raise RuntimeError(f"Another chaos experiment ({self.active_experiment['id']}) is already active. Please wait or cancel it first.")

        exp_id = f"exp-{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        exp: Dict[str, Any] = {
            "id": exp_id,
            "type": exp_type,
            "target_service": target_service,
            "parameters": params,
            "status": "PENDING",
            "start_timestamp": now_iso,
            "failure_timestamp": None,
            "detection_timestamp": None,
            "recovery_start_timestamp": None,
            "recovery_timestamp": None,
            "detection_time_ms": None,
            "recovery_duration_ms": None,
            "total_downtime_ms": None,
            "recovery_outcome": None,
            "error_details": None,
            "logs": []
        }

        self.active_experiment = exp
        self._log_event(exp, f"Experiment registered: {exp_type} against {target_service}")
        models.save_experiment(exp)

        # Launch async task in background
        asyncio.create_task(self.run_experiment_lifecycle(exp))
        return exp

    def cancel_active_experiment(self, exp_id: str) -> bool:
        if self.active_experiment and self.active_experiment["id"] == exp_id:
            logger.info(f"Cancellation requested for active experiment {exp_id}")
            self._cancel_event.set()
            return True
        return False

    async def poll_service_health(self):
        """Background health poller running periodically."""
        services = [
            ("product-service", settings.PRODUCT_SERVICE_URL),
            ("order-service", settings.ORDER_SERVICE_URL)
        ]

        for s_id, s_url in services:
            t0 = asyncio.get_event_loop().time()
            status = "HEALTHY"
            http_code = None
            details = {}
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"{s_url}/health")
                    http_code = resp.status_code
                    latency = round((asyncio.get_event_loop().time() - t0) * 1000, 2)
                    if resp.status_code == 200:
                        details = resp.json()
                        status = "HEALTHY" if details.get("status") == "healthy" else "DEGRADED"
                    elif resp.status_code == 503:
                        status = "UNHEALTHY"
                        try:
                            details = resp.json()
                        except Exception:
                            details = {"error": resp.text}
                    else:
                        status = "DEGRADED"
            except httpx.ConnectError:
                latency = round((asyncio.get_event_loop().time() - t0) * 1000, 2)
                status = "DOWN"
                details = {"error": "Connection refused"}
            except Exception as e:
                latency = round((asyncio.get_event_loop().time() - t0) * 1000, 2)
                status = "DOWN"
                details = {"error": str(e)}

            now_iso = datetime.now(timezone.utc).isoformat()
            prev_status = self.service_health_cache[s_id]["status"]

            if prev_status == "HEALTHY" and status in ("UNHEALTHY", "DOWN", "DEGRADED"):
                self.service_health_cache[s_id]["last_failure"] = now_iso
            elif prev_status in ("UNHEALTHY", "DOWN", "DEGRADED") and status == "HEALTHY":
                self.service_health_cache[s_id]["last_recovery"] = now_iso

            self.service_health_cache[s_id]["status"] = status
            self.service_health_cache[s_id]["http_status"] = http_code
            self.service_health_cache[s_id]["latency_ms"] = latency
            self.service_health_cache[s_id]["last_checked"] = now_iso
            self.service_health_cache[s_id]["details"] = details


chaos_engine = ChaosEngine()
