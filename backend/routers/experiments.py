"""Experiment execution, status tracking, and history API endpoints."""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from backend import models
from backend.schemas import ExperimentCreate, ExperimentResponse
from backend.chaos.engine import chaos_engine
from backend.config import settings

router = APIRouter(prefix="/api/experiments", tags=["Chaos Experiments"])


@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED, summary="Trigger Chaos Experiment")
async def trigger_experiment(req: ExperimentCreate):
    """Initiates a controlled failure injection on the designated microservice.
    
    Requires explicit user confirmation (`confirm_destruction: true`).
    """
    if req.target_service not in settings.ALLOWED_TARGET_SERVICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target service '{req.target_service}' is not in allowed target services: {settings.ALLOWED_TARGET_SERVICES}"
        )

    # Validate limits
    if req.duration_seconds > settings.MAX_EXPERIMENT_DURATION_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duration exceeds maximum allowed limit of {settings.MAX_EXPERIMENT_DURATION_SECONDS} seconds"
        )
    if req.load_percent and req.load_percent > settings.MAX_CPU_LOAD_PERCENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CPU load exceeds safety threshold of {settings.MAX_CPU_LOAD_PERCENT}%"
        )
    if req.memory_mb and req.memory_mb > settings.MAX_MEMORY_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Memory allocation exceeds safety limit of {settings.MAX_MEMORY_MB} MB"
        )

    params = req.model_dump()
    params.pop("type")
    params.pop("target_service")
    params.pop("confirm_destruction")

    try:
        exp = chaos_engine.start_experiment(
            exp_type=req.type,
            target_service=req.target_service,
            params=params
        )
        return exp
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("", response_model=List[ExperimentResponse], summary="List Experiment History")
async def list_experiment_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None, description="Filter by experiment type"),
    target_service: Optional[str] = Query(None, description="Filter by target service"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Retrieve historical chaos experiments with pagination and filtering."""
    return models.list_experiments(
        limit=limit,
        offset=offset,
        exp_type=type,
        target_service=target_service,
        status=status
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse, summary="Get Experiment Details")
async def get_experiment(experiment_id: str):
    """Retrieve detailed execution trace, timestamps, metrics, and logs for an experiment."""
    # If active, get current in-memory progress
    if chaos_engine.active_experiment and chaos_engine.active_experiment["id"] == experiment_id:
        return chaos_engine.active_experiment

    exp = models.get_experiment_by_id(experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found")
    return exp


@router.post("/{experiment_id}/cancel", summary="Cancel Running Experiment")
async def cancel_experiment(experiment_id: str):
    """Cancel an active chaos experiment and immediately trigger recovery."""
    success = chaos_engine.cancel_active_experiment(experiment_id)
    if not success:
        exp = models.get_experiment_by_id(experiment_id)
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experiment '{experiment_id}' is not currently running (status: {exp['status']})"
        )
    return {"message": f"Cancellation requested for experiment {experiment_id}", "status": "cancelling"}
