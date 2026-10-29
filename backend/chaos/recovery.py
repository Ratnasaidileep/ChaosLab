"""Automatic recovery and verified health restoration for ChaosLab."""
import time
import asyncio
import logging
from typing import Dict, Any, Tuple
import httpx

from backend.config import settings
from backend.chaos.docker_client import docker_controller
from backend.chaos.injectors import get_service_url

logger = logging.getLogger("chaoslab.recovery")


async def execute_recovery_action(
    target_service: str,
    exp_type: str,
    injection_mode: str = "http_simulation"
) -> Dict[str, Any]:
    """Trigger the recovery mechanism for a failed service."""
    logger.info(f"Triggering recovery for {target_service} (type: {exp_type}, mode: {injection_mode})")
    service_url = get_service_url(target_service)
    results = {}

    # If Docker container was stopped, restart it
    if exp_type == "container_failure" and injection_mode == "docker":
        try:
            docker_res = docker_controller.start_container(target_service)
            results["docker"] = docker_res
        except Exception as e:
            logger.error(f"Docker container restart failed: {e}")
            results["docker_error"] = str(e)

    # In all cases, call the service's recovery hook to clear internal state / buffers / flags
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{service_url}/_chaos/recover")
            results["http_recover"] = resp.json() if resp.status_code == 200 else resp.text
    except Exception as e:
        logger.debug(f"HTTP recovery hook call warning (service might still be restarting): {e}")
        results["http_recover_initial_exception"] = str(e)

    return results


async def verify_service_health(
    target_service: str,
    timeout_seconds: float = 30.0,
    poll_interval: float = 1.0
) -> Tuple[bool, Dict[str, Any]]:
    """Poll the target service's /health endpoint until it verifies healthy or times out.
    
    Never claims a service recovered without a successful health check!
    """
    service_url = get_service_url(target_service)
    start_time = time.time()
    last_error = ""

    while (time.time() - start_time) < timeout_seconds:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{service_url}/health")
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "healthy":
                        duration = time.time() - start_time
                        logger.info(f"Verified health for {target_service} in {duration:.2f}s")
                        return True, {
                            "status": "healthy",
                            "verification_time_seconds": round(duration, 2),
                            "health_payload": data
                        }
                    else:
                        last_error = f"Service responded with status: {data.get('status')}"
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
        except Exception as exc:
            last_error = f"Connection error: {str(exc)}"

        await asyncio.sleep(poll_interval)

    logger.warning(f"Recovery verification timed out for {target_service} after {timeout_seconds}s. Last error: {last_error}")
    return False, {
        "status": "unhealthy",
        "error": f"Verification timed out after {timeout_seconds}s. Last error: {last_error}"
    }
