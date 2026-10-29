"""Tests for Product Service."""
import pytest
from fastapi.testclient import TestClient

from services.product_service.main import app, chaos_state
from services.product_service import database


@pytest.fixture(autouse=True)
def reset_service_state():
    """Reset database and chaos state before each test."""
    chaos_state.is_outage = False
    chaos_state.latency_ms = 0
    chaos_state.active_type = None
    chaos_state.cpu_stop_event.set()
    chaos_state.memory_buffer.clear()
    database.init_db()
    yield


client = TestClient(app)


def test_health_check_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "product-service"
    assert data["database"] == "connected"


def test_list_products():
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 6
    assert any(p["name"] == "Laptop Pro 15" for p in products)


def test_get_product_by_id():
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "Laptop Pro" in data["name"]

    response_404 = client.get("/products/9999")
    assert response_404.status_code == 404


def test_reserve_stock_success_and_failure():
    res = client.post("/products/1/reserve", json={"quantity": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["reserved"] is True

    res_fail = client.post("/products/1/reserve", json={"quantity": 9999})
    assert res_fail.status_code == 400
    assert "Insufficient stock" in res_fail.json()["detail"]


def test_chaos_outage_injection_and_recovery():
    res_inject = client.post("/_chaos/inject", json={"type": "outage"})
    assert res_inject.status_code == 200
    assert res_inject.json()["status"] == "injected"

    res_health = client.get("/health")
    assert res_health.status_code == 503
    assert res_health.json()["status"] == "unhealthy"

    res_products = client.get("/products")
    assert res_products.status_code == 503

    res_recover = client.post("/_chaos/recover")
    assert res_recover.status_code == 200
    assert res_recover.json()["health"] == "healthy"

    res_health_after = client.get("/health")
    assert res_health_after.status_code == 200
    assert res_health_after.json()["status"] == "healthy"


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "product_service_requests_total" in response.text
