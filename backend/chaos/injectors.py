"""Failure Injection Engine for ChaosLab."""
import logging
from typing import Dict, Any
import httpx

from backend.config import settings
from backend.chaos.docker_client import docker_controller

logger = logging.getLogger("chaoslab.injectors")


def get_service_url(target_service: str) -> str:
    if target_service == "product-service":
        return settings.PRODUCT_SERVICE_URL
    elif target_service == "order-service":
        return settings.ORDER_SERVICE_URL
    else:
        raise ValueError(f"Unknown service '{target_service}'")


async def inject_failure(
    exp_id: str,
    exp_type: str,
    target_service: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute failure injection based on experiment type."""
    logger.info(f"Injecting {exp_type} on {target_service} (Experiment ID: {exp_id})")
    service_url = get_service_url(target_service)

    if exp_type == "container_failure":
        # Check if Docker mode is available and enabled
        if settings.ENABLE_DOCKER_CHAOS and docker_controller.is_docker_available():
            try:
                res = docker_controller.stop_container(target_service)
                return {
                    "mode": "docker",
                    "details": res,
                    "target_service": target_service
                }
            except Exception as e:
                logger.warning(f"Docker stop failed ({e}), falling back to HTTP outage simulation")

        # Fallback to HTTP outage simulation
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{service_url}/_chaos/inject", json={"type": "outage"})
            return {
                "mode": "http_simulation",
                "details": resp.json(),
                "target_service": target_service
            }

    elif exp_type == "cpu_stress":
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{service_url}/_chaos/inject",
                json={
                    "type": "cpu",
                    "duration_seconds": params.get("duration_seconds", 15),
                    "load_percent": params.get("load_percent", 70)
                }
            )
            return {
                "mode": "http_stress",
                "details": resp.json(),
                "target_service": target_service
            }

    elif exp_type == "memory_stress":
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{service_url}/_chaos/inject",
                json={
                    "type": "memory",
                    "duration_seconds": params.get("duration_seconds", 15),
                    "memory_mb": params.get("memory_mb", 150)
                }
            )
            return {
                "mode": "http_stress",
                "details": resp.json(),
                "target_service": target_service
            }

    elif exp_type == "dependency_failure":
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{service_url}/_chaos/inject",
                json={"type": "dependency_failure"}
            )
            return {
                "mode": "dependency_simulation",
                "details": resp.json(),
                "target_service": target_service
            }

    elif exp_type == "network_delay":
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{service_url}/_chaos/inject",
                json={
                    "type": "latency",
                    "delay_ms": params.get("delay_ms", 1000),
                    "duration_seconds": params.get("duration_seconds", 15)
                }
            )
            return {
                "mode": "latency_simulation",
                "details": resp.json(),
                "target_service": target_service
            }

    else:
        raise ValueError(f"Unsupported experiment type '{exp_type}'")
