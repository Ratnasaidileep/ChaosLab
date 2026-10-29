"""Unit tests for experiment validation and security rules."""
import pytest
from pydantic import ValidationError
from backend.schemas import ExperimentCreate


def test_valid_experiment_create():
    exp = ExperimentCreate(
        type="cpu_stress",
        target_service="product-service",
        duration_seconds=20,
        load_percent=60,
        confirm_destruction=True
    )
    assert exp.type == "cpu_stress"
    assert exp.target_service == "product-service"
    assert exp.confirm_destruction is True


def test_reject_missing_confirmation():
    with pytest.raises(ValidationError) as excinfo:
        ExperimentCreate(
            type="container_failure",
            target_service="product-service",
            confirm_destruction=False
        )
    assert "confirm_destruction must be True" in str(excinfo.value)


def test_reject_unsupported_experiment_type():
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="unsupported_chaos",  # Invalid type
            target_service="product-service",
            confirm_destruction=True
        )


def test_reject_unauthorized_target_service():
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="cpu_stress",
            target_service="payment-service",  # Not in allowlist
            confirm_destruction=True
        )


def test_reject_duration_out_of_bounds():
    # Below minimum (5s)
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="cpu_stress",
            target_service="product-service",
            duration_seconds=2,
            confirm_destruction=True
        )

    # Above maximum (60s)
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="cpu_stress",
            target_service="product-service",
            duration_seconds=120,
            confirm_destruction=True
        )


def test_reject_cpu_and_memory_safety_limits():
    # CPU over 80%
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="cpu_stress",
            target_service="product-service",
            load_percent=95,
            confirm_destruction=True
        )

    # Memory over 350MB
    with pytest.raises(ValidationError):
        ExperimentCreate(
            type="memory_stress",
            target_service="product-service",
            memory_mb=500,
            confirm_destruction=True
        )
