"""Tests for Order Service."""
import pytest
from fastapi.testclient import TestClient

from services.order_service.main import app, chaos_state
from services.order_service import database


@pytest.fixture(autouse=True)
def reset_service_state():
    """Reset database and chaos state before each test."""
    chaos_state.is_outage = False
    chaos_state.dependency_failure = False
    chaos_state.latency_ms = 0
    chaos_state.active_type = None
    chaos_state.cpu_stop_event.set()
    chaos_state.memory_buffer.clear()
    database.init_db()
    yield


client = TestClient(app)


def test_list_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 2
    assert any(o["order_number"] == "ORD-7001" for o in orders)


def test_get_order_by_id():
    response = client.get("/orders/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["customer_name"] == "Alice Smith"

    response_404 = client.get("/orders/9999")
    assert response_404.status_code == 404


def test_dependency_failure_injection_and_recovery():
    # Inject dependency failure
    res_inject = client.post("/_chaos/inject", json={"type": "dependency_failure"})
    assert res_inject.status_code == 200
    assert res_inject.json()["status"] == "injected"

    # Health check should return degraded / 503
    res_health = client.get("/health")
    assert res_health.status_code == 503
    assert "UNAVAILABLE" in res_health.json()["dependencies"]["product_service"]

    # Order creation should fail with 503
    order_payload = {
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    res_order = client.post("/orders", json=order_payload)
    assert res_order.status_code == 503

    # Recover
    res_recover = client.post("/_chaos/recover")
    assert res_recover.status_code == 200
    assert res_recover.json()["health"] == "healthy"


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "order_service_requests_total" in response.text
