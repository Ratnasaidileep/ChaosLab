"""Order Service for ChaosLab demonstration.

Handles order creation, inventory reservation coordination with Product Service,
Prometheus telemetry, and controlled chaos hooks.
"""
import os
import time
import asyncio
import threading
import psutil
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

try:
    from .models import CreateOrderRequest, Order, ChaosInjectionRequest
    from . import database
except ImportError:
    from models import CreateOrderRequest, Order, ChaosInjectionRequest
    import database

# Initialize database
database.init_db()

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001").rstrip("/")

app = FastAPI(
    title="Order Service",
    description="Order Processing Service with Dependency Resilience for ChaosLab",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "order_service_requests_total",
    "Total HTTP requests handled by Order Service",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "order_service_request_duration_seconds",
    "HTTP request latency in seconds for Order Service",
    ["endpoint"]
)
DEPENDENCY_ERRORS = Counter(
    "order_service_dependency_errors_total",
    "Count of failed outbound calls to downstream dependencies",
    ["target_dependency", "error_type"]
)
CHAOS_ACTIVE = Gauge(
    "order_service_chaos_active",
    "Indicates if a chaos experiment is currently active on Order Service (1=active, 0=inactive)",
    ["type"]
)
SERVICE_HEALTH = Gauge(
    "order_service_health_status",
    "Health status of Order Service (1=healthy, 0=degraded/down)"
)
SERVICE_HEALTH.set(1)

# In-memory Chaos State
class ChaosState:
    def __init__(self):
        self.is_outage: bool = False
        self.dependency_failure: bool = False
        self.latency_ms: int = 0
        self.active_type: Optional[str] = None
        self.injected_at: Optional[str] = None
        self.cpu_stop_event = threading.Event()
        self.cpu_threads: List[threading.Thread] = []
        self.memory_buffer: List[bytes] = []

chaos_state = ChaosState()


@app.middleware("http")
async def metrics_and_chaos_middleware(request: Request, call_next):
    is_management_route = request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/_chaos")

    if chaos_state.is_outage and not is_management_route:
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code="503").inc()
        return Response(
            content='{"error": "Service Unavailable", "detail": "ChaosLab: Simulated Service Outage active"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    if chaos_state.latency_ms > 0 and not is_management_route:
        await asyncio.sleep(chaos_state.latency_ms / 1000.0)

    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
        return response
    except Exception as exc:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code="500").inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
        raise exc


# ------------------------------------------------------------------------------
# Business API Endpoints
# ------------------------------------------------------------------------------

@app.get("/health", summary="Health Check")
async def health_check():
    """Health check reporting internal state and downstream Product Service dependency."""
    if chaos_state.is_outage:
        SERVICE_HEALTH.set(0)
        return Response(
            content='{"status": "unhealthy", "service": "order-service", "reason": "Simulated outage active"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    product_service_status = "ok"
    if chaos_state.dependency_failure:
        product_service_status = "injected_failure"
        SERVICE_HEALTH.set(0)
        return Response(
            content='{"status": "degraded", "service": "order-service", "dependencies": {"product_service": "UNAVAILABLE (Chaos Injected)"}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    # Probe product-service dependency
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/health")
            if resp.status_code != 200:
                product_service_status = f"unhealthy ({resp.status_code})"
    except Exception as e:
        product_service_status = f"unreachable ({str(e)})"

    is_healthy = product_service_status == "ok"
    SERVICE_HEALTH.set(1 if is_healthy else 0)

    res_body = {
        "status": "healthy" if is_healthy else "degraded",
        "service": "order-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "product_service": product_service_status
        },
        "active_chaos": chaos_state.active_type,
        "metrics": {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_mb": round(psutil.Process().memory_info().rss / (1024 * 1024), 2)
        }
    }

    if not is_healthy:
        return Response(
            content=str(res_body).replace("'", '"'),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )
    return res_body


@app.get("/metrics", summary="Prometheus Metrics")
async def metrics():
    """Exposes Prometheus scrape metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/orders", response_model=List[Order], summary="List Orders")
async def get_orders():
    """Retrieve all orders."""
    return database.list_orders()


@app.get("/orders/{order_id}", response_model=Order, summary="Get Order Details")
async def get_order(order_id: int):
    """Retrieve a single order by its ID."""
    order = database.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@app.post("/orders", response_model=Order, status_code=201, summary="Create New Order")
async def create_new_order(request: CreateOrderRequest):
    """Create a new order and reserve stock from the Product Service."""
    if chaos_state.dependency_failure:
        DEPENDENCY_ERRORS.labels(target_dependency="product-service", error_type="SimulatedPartition").inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Downstream dependency product-service is unreachable (ChaosLab injected dependency failure)"
        )

    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    confirmed_items = []
    total_amount = 0.0

    async with httpx.AsyncClient(timeout=4.0) as client:
        for item in request.items:
            # 1. Fetch product
            try:
                prod_resp = await client.get(f"{PRODUCT_SERVICE_URL}/products/{item.product_id}")
                if prod_resp.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} does not exist")
                if prod_resp.status_code != 200:
                    DEPENDENCY_ERRORS.labels(target_dependency="product-service", error_type="HTTPError").inc()
                    raise HTTPException(status_code=502, detail=f"Product Service returned {prod_resp.status_code}")
                prod_data = prod_resp.json()
            except httpx.RequestError as exc:
                DEPENDENCY_ERRORS.labels(target_dependency="product-service", error_type="ConnectionError").inc()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to communicate with Product Service: {str(exc)}"
                )

            # 2. Reserve stock
            try:
                res_resp = await client.post(
                    f"{PRODUCT_SERVICE_URL}/products/{item.product_id}/reserve",
                    json={"quantity": item.quantity}
                )
                if res_resp.status_code != 200:
                    err_msg = res_resp.json().get("detail", "Stock reservation failed")
                    raise HTTPException(status_code=400, detail=f"Cannot order {prod_data['name']}: {err_msg}")
            except httpx.RequestError as exc:
                DEPENDENCY_ERRORS.labels(target_dependency="product-service", error_type="ReservationTimeout").inc()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Stock reservation request failed: {str(exc)}"
                )

            item_cost = prod_data["price"] * item.quantity
            total_amount += item_cost
            confirmed_items.append({
                "product_id": item.product_id,
                "product_name": prod_data["name"],
                "quantity": item.quantity,
                "price": prod_data["price"]
            })

    # Record order in SQLite
    order = database.create_order(
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        items=confirmed_items,
        total_amount=round(total_amount, 2)
    )
    return order


# ------------------------------------------------------------------------------
# Chaos Engineering Injection & Recovery Hooks
# ------------------------------------------------------------------------------

def _cpu_worker(stop_event: threading.Event):
    while not stop_event.is_set():
        _ = [x ** 2 for x in range(1000)]
        time.sleep(0.001)


@app.post("/_chaos/inject", summary="Inject Controlled Chaos")
async def inject_chaos(req: ChaosInjectionRequest):
    chaos_type = req.type.lower()
    chaos_state.active_type = chaos_type
    chaos_state.injected_at = datetime.now(timezone.utc).isoformat()

    if chaos_type == "dependency_failure":
        chaos_state.dependency_failure = True
        SERVICE_HEALTH.set(0)
        CHAOS_ACTIVE.labels(type="dependency_failure").set(1)

    elif chaos_type == "outage":
        chaos_state.is_outage = True
        SERVICE_HEALTH.set(0)
        CHAOS_ACTIVE.labels(type="outage").set(1)

    elif chaos_type == "latency":
        chaos_state.latency_ms = req.delay_ms or 1000
        CHAOS_ACTIVE.labels(type="latency").set(1)

    elif chaos_type == "cpu":
        chaos_state.cpu_stop_event.clear()
        num_threads = min(max(1, (psutil.cpu_count() or 2) - 1), 3)
        chaos_state.cpu_threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=_cpu_worker, args=(chaos_state.cpu_stop_event,), daemon=True)
            t.start()
            chaos_state.cpu_threads.append(t)
        CHAOS_ACTIVE.labels(type="cpu").set(1)

        if req.duration_seconds and req.duration_seconds > 0:
            def _auto_stop():
                time.sleep(req.duration_seconds)
                chaos_state.cpu_stop_event.set()
                CHAOS_ACTIVE.labels(type="cpu").set(0)
                if chaos_state.active_type == "cpu":
                    chaos_state.active_type = None
            threading.Thread(target=_auto_stop, daemon=True).start()

    elif chaos_type == "memory":
        target_mb = min(req.memory_mb or 150, 350)
        chunk_size = 10 * 1024 * 1024
        chaos_state.memory_buffer = []
        for _ in range(target_mb // 10):
            chaos_state.memory_buffer.append(b"x" * chunk_size)
        CHAOS_ACTIVE.labels(type="memory").set(1)

        if req.duration_seconds and req.duration_seconds > 0:
            def _auto_free():
                time.sleep(req.duration_seconds)
                chaos_state.memory_buffer.clear()
                CHAOS_ACTIVE.labels(type="memory").set(0)
                if chaos_state.active_type == "memory":
                    chaos_state.active_type = None
            threading.Thread(target=_auto_free, daemon=True).start()

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported chaos type: {req.type}")

    return {
        "status": "injected",
        "type": chaos_type,
        "service": "order-service",
        "injected_at": chaos_state.injected_at,
        "parameters": req.model_dump()
    }


@app.post("/_chaos/recover", summary="Recover from Chaos")
async def recover_chaos():
    """Immediately restores Order Service to a healthy baseline."""
    chaos_state.cpu_stop_event.set()
    chaos_state.cpu_threads.clear()
    chaos_state.memory_buffer.clear()

    chaos_state.is_outage = False
    chaos_state.dependency_failure = False
    chaos_state.latency_ms = 0
    chaos_state.active_type = None
    chaos_state.injected_at = None

    SERVICE_HEALTH.set(1)
    for t in ["dependency_failure", "outage", "latency", "cpu", "memory"]:
        CHAOS_ACTIVE.labels(type=t).set(0)

    return {
        "status": "recovered",
        "service": "order-service",
        "recovered_at": datetime.now(timezone.utc).isoformat(),
        "health": "healthy"
    }


@app.get("/_chaos/status", summary="Current Chaos Status")
async def chaos_status():
    return {
        "service": "order-service",
        "active_type": chaos_state.active_type,
        "is_outage": chaos_state.is_outage,
        "dependency_failure": chaos_state.dependency_failure,
        "latency_ms": chaos_state.latency_ms,
        "cpu_workers_active": len(chaos_state.cpu_threads) if not chaos_state.cpu_stop_event.is_set() else 0,
        "memory_allocated_mb": len(chaos_state.memory_buffer) * 10,
        "injected_at": chaos_state.injected_at
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
