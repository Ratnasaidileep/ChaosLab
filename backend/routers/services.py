"""Service Management & Health Inspection API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from backend.schemas import ServiceHealth
from backend.chaos.engine import chaos_engine
from backend.chaos.recovery import verify_service_health

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=List[ServiceHealth], summary="List Monitored Services")
async def list_services():
    """Returns the list of monitored microservices and their health status."""
    return list(chaos_engine.service_health_cache.values())


@router.get("/{service_id}/health", response_model=ServiceHealth, summary="Get Service Health")
async def get_service_health(service_id: str):
    """Retrieve detailed health check for a specific service."""
    if service_id not in chaos_engine.service_health_cache:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' is not in monitored services")
    return chaos_engine.service_health_cache[service_id]


@router.post("/{service_id}/verify", summary="Verify Service Health On-Demand")
async def verify_service(service_id: str):
    """Actively trigger a health check against a service."""
    if service_id not in chaos_engine.service_health_cache:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' is not registered")

    verified, details = await verify_service_health(service_id, timeout_seconds=5.0)
    await chaos_engine.poll_service_health()
    return {
        "service_id": service_id,
        "verified": verified,
        "details": details,
        "current_status": chaos_engine.service_health_cache[service_id]["status"]
    }
