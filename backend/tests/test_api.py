"""Integration tests for ChaosLab REST API endpoints."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend import models

client = TestClient(app)


@pytest.fixture(autouse=True)
def init_test_db():
    models.init_db()
    yield


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chaoslab-backend"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "chaoslab_system_health" in response.text


def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_system_health"] in ["HEALTHY", "DEGRADED", "UNHEALTHY"]
    assert "product-service" in data["services"]
    assert "order-service" in data["services"]
    assert "total_experiments" in data


def test_dashboard_analysis():
    response = client.get("/api/dashboard/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "timeline_series" in data
    assert "type_breakdown" in data


def test_list_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 2
    service_ids = [s["id"] for s in services]
    assert "product-service" in service_ids
    assert "order-service" in service_ids


def test_get_service_health():
    response = client.get("/api/services/product-service/health")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "product-service"
    assert "status" in data

    # 404 for unknown service
    res_404 = client.get("/api/services/unknown-svc/health")
    assert res_404.status_code == 404


def test_experiment_crud_and_validation():
    # Attempt without confirmation
    bad_req = {
        "type": "cpu_stress",
        "target_service": "product-service",
        "confirm_destruction": False
    }
    res_bad = client.post("/api/experiments", json=bad_req)
    assert res_bad.status_code == 422  # Pydantic validation error

    # Valid experiment insertion into database for history checking
    mock_exp = {
        "id": "exp-test001",
        "type": "cpu_stress",
        "target_service": "product-service",
        "parameters": {"duration_seconds": 10},
        "status": "RECOVERED",
        "start_timestamp": "2026-10-28T12:00:00Z",
        "failure_timestamp": "2026-10-28T12:00:01Z",
        "detection_timestamp": "2026-10-28T12:00:02Z",
        "recovery_start_timestamp": "2026-10-28T12:00:11Z",
        "recovery_timestamp": "2026-10-28T12:00:13Z",
        "detection_time_ms": 1000.0,
        "recovery_duration_ms": 2000.0,
        "total_downtime_ms": 12000.0,
        "recovery_outcome": "SUCCESS",
        "error_details": None,
        "logs": [{"timestamp": "2026-10-28T12:00:00Z", "level": "INFO", "message": "Test completed"}]
    }
    models.save_experiment(mock_exp)

    # Fetch history
    history_res = client.get("/api/experiments")
    assert history_res.status_code == 200
    exps = history_res.json()
    assert len(exps) >= 1
    assert any(e["id"] == "exp-test001" for e in exps)

    # Fetch details
    detail_res = client.get("/api/experiments/exp-test001")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == "exp-test001"
    assert detail["status"] == "RECOVERED"
    assert detail["recovery_duration_ms"] == 2000.0
    assert len(detail["logs"]) == 1

    # 404 for non-existent experiment
    res_404 = client.get("/api/experiments/non-existent-id")
    assert res_404.status_code == 404
