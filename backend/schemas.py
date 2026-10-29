"""Pydantic schemas and validation for ChaosLab API."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

ExperimentType = Literal[
    "container_failure",
    "cpu_stress",
    "memory_stress",
    "dependency_failure",
    "network_delay"
]

TargetService = Literal[
    "product-service",
    "order-service"
]

ExperimentStatus = Literal[
    "PENDING",
    "INJECTING",
    "RUNNING",
    "DETECTED",
    "RECOVERING",
    "VERIFYING",
    "RECOVERED",
    "FAILED",
    "CANCELLED"
]


class ExperimentCreate(BaseModel):
    type: ExperimentType = Field(..., description="Type of controlled failure to inject")
    target_service: TargetService = Field(..., description="Target microservice (product-service or order-service)")
    duration_seconds: int = Field(15, ge=5, le=60, description="Duration in seconds before auto-recovery (5 to 60)")
    load_percent: Optional[int] = Field(70, ge=10, le=80, description="CPU workload percentage (10 to 80)")
    memory_mb: Optional[int] = Field(150, ge=50, le=350, description="Memory consumption in MB (50 to 350)")
    delay_ms: Optional[int] = Field(1000, ge=100, le=3000, description="Artificial network delay in ms (100 to 3000)")
    confirm_destruction: bool = Field(..., description="User explicit confirmation required for controlled failure injection")

    @field_validator("confirm_destruction")
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Controlled failure injection requires explicit user confirmation (confirm_destruction must be True)")
        return v


class ExperimentResponse(BaseModel):
    id: str
    type: str
    target_service: str
    parameters: Dict[str, Any]
    status: str
    start_timestamp: str
    failure_timestamp: Optional[str] = None
    detection_timestamp: Optional[str] = None
    recovery_start_timestamp: Optional[str] = None
    recovery_timestamp: Optional[str] = None
    detection_time_ms: Optional[float] = None
    recovery_duration_ms: Optional[float] = None
    total_downtime_ms: Optional[float] = None
    recovery_outcome: Optional[str] = None
    error_details: Optional[str] = None
    logs: List[Dict[str, Any]] = []


class ServiceHealth(BaseModel):
    id: str
    name: str
    url: str
    status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY", "DOWN"]
    http_status: Optional[int] = None
    latency_ms: Optional[float] = None
    last_checked: str
    last_failure: Optional[str] = None
    last_recovery: Optional[str] = None
    details: Dict[str, Any] = {}


class DashboardSummary(BaseModel):
    overall_system_health: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"]
    services: Dict[str, ServiceHealth]
    total_experiments: int
    successful_recoveries: int
    failed_recoveries: int
    recovery_success_rate_percent: float
    avg_recovery_duration_ms: Optional[float] = None
    avg_detection_time_ms: Optional[float] = None
    avg_total_downtime_ms: Optional[float] = None
    active_experiment: Optional[ExperimentResponse] = None
