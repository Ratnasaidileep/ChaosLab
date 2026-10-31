"""Product Service for ChaosLab demonstration.

Exposes REST APIs for product catalog, stock reservation, Prometheus metrics,
and controlled chaos hooks for resilience testing.
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
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

try:
    from .models import Product, StockReservationRequest, StockReservationResponse, ChaosInjectionRequest
    from . import database
except ImportError:
    from models import Product, StockReservationRequest, StockReservationResponse, ChaosInjectionRequest
    import database

# Initialize database
database.init_db()

app = FastAPI(
    title="Product Service",
    description="Product Catalog & Stock Management Service for ChaosLab",
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
    "product_service_requests_total",
    "Total HTTP requests handled by Product Service",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "product_service_request_duration_seconds",
    "HTTP request latency in seconds for Product Service",
    ["endpoint"]
)
CHAOS_ACTIVE = Gauge(
    "product_service_chaos_active",
    "Indicates if a chaos experiment is currently active on Product Service (1=active, 0=inactive)",
    ["type"]
)
SERVICE_HEALTH = Gauge(
    "product_service_health_status",
    "Health status of Product Service (1=healthy, 0=degraded/down)"
)
SERVICE_HEALTH.set(1)

# In-memory Chaos State
class ChaosState:
    def __init__(self):
        self.is_outage: bool = False
        self.outage_reason: str = ""
        self.latency_ms: int = 0
        self.active_type: Optional[str] = None
        self.experiment_id: Optional[str] = None
        self.cpu_stop_event = threading.Event()
        self.cpu_threads: List[threading.Thread] = []
        self.memory_buffer: List[bytes] = []
        self.injected_at: Optional[str] = None

chaos_state = ChaosState()


@app.middleware("http")
async def metrics_and_chaos_middleware(request: Request, call_next):
    # Skip chaos for health endpoints, metrics, and chaos management itself
    is_management_route = request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/_chaos")

    # If outage is active and not an internal management route, reject with 503
    if chaos_state.is_outage and not is_management_route:
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code="503").inc()
        return Response(
            content='{"error": "Service Unavailable", "detail": "ChaosLab: Simulated Service Outage active"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    # If artificial latency is active
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
    """Returns the operational health of the Product Service."""
    if chaos_state.is_outage:
        SERVICE_HEALTH.set(0)
        return Response(
            content='{"status": "unhealthy", "service": "product-service", "reason": "Simulated outage active"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    if chaos_state.active_type in ["cpu", "memory", "latency"]:
        SERVICE_HEALTH.set(0)
        return Response(
            content=f'{{"status": "degraded", "service": "product-service", "reason": "Chaos active: {chaos_state.active_type}", "active_chaos": "{chaos_state.active_type}"}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    SERVICE_HEALTH.set(1)
    return {
        "status": "healthy",
        "service": "product-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
        "active_chaos": None,
        "metrics": {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_mb": round(psutil.Process().memory_info().rss / (1024 * 1024), 2)
        }
    }


@app.get("/metrics", summary="Prometheus Metrics")
async def metrics():
    """Exposes Prometheus scrape metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/products", response_model=List[Product], summary="List Products")
async def get_products():
    """Retrieve all available products."""
    return database.list_products()


@app.get("/products/{product_id}", response_model=Product, summary="Get Product Details")
async def get_product(product_id: int):
    """Retrieve a single product by its ID."""
    product = database.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product


@app.post("/products/{product_id}/reserve", response_model=StockReservationResponse, summary="Reserve Stock")
async def reserve_stock(product_id: int, request: StockReservationRequest):
    """Reserve stock for an order."""
    result = database.reserve_stock(product_id, request.quantity)
    if not result["reserved"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {
        "product_id": product_id,
        "reserved": True,
        "remaining_stock": result["remaining_stock"],
        "message": result["message"]
    }


@app.post("/products/{product_id}/release", response_model=StockReservationResponse, summary="Release Stock")
async def release_stock(product_id: int, request: StockReservationRequest):
    """Release previously reserved stock back to inventory."""
    result = database.release_stock(product_id, request.quantity)
    return {
        "product_id": product_id,
        "reserved": False,
        "remaining_stock": result["remaining_stock"],
        "message": result["message"]
    }


# ------------------------------------------------------------------------------
# Chaos Engineering Injection & Recovery Hooks
# ------------------------------------------------------------------------------

def _cpu_worker(stop_event: threading.Event):
    """Busy worker thread to generate bounded CPU load."""
    while not stop_event.is_set():
        _ = [x ** 2 for x in range(1000)]
        time.sleep(0.001)


@app.post("/_chaos/inject", summary="Inject Controlled Chaos")
async def inject_chaos(req: ChaosInjectionRequest):
    """Inject controlled failures for resilience testing."""
    chaos_type = req.type.lower()
    chaos_state.active_type = chaos_type
    chaos_state.injected_at = datetime.now(timezone.utc).isoformat()

    if chaos_type == "outage":
        chaos_state.is_outage = True
        chaos_state.outage_reason = "Manual chaos injection: simulated service outage"
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

        # Auto stop after duration if specified
        if req.duration_seconds and req.duration_seconds > 0:
            def _auto_stop():
                time.sleep(req.duration_seconds)
                chaos_state.cpu_stop_event.set()
                CHAOS_ACTIVE.labels(type="cpu").set(0)
                if chaos_state.active_type == "cpu":
                    chaos_state.active_type = None
            threading.Thread(target=_auto_stop, daemon=True).start()

    elif chaos_type == "memory":
        target_mb = min(req.memory_mb or 150, 350)  # Bound to max 350MB
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
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
        "service": "product-service",
        "injected_at": chaos_state.injected_at,
        "parameters": req.model_dump()
    }


@app.post("/_chaos/recover", summary="Recover from Chaos")
async def recover_chaos():
    """Immediately restores Product Service to a healthy baseline."""
    # Stop CPU threads
    chaos_state.cpu_stop_event.set()
    chaos_state.cpu_threads.clear()

    # Free memory buffer
    chaos_state.memory_buffer.clear()

    # Reset outage and latency flags
    chaos_state.is_outage = False
    chaos_state.latency_ms = 0
    chaos_state.active_type = None
    chaos_state.injected_at = None

    # Reset metrics
    SERVICE_HEALTH.set(1)
    for t in ["outage", "latency", "cpu", "memory"]:
        CHAOS_ACTIVE.labels(type=t).set(0)

    return {
        "status": "recovered",
        "service": "product-service",
        "recovered_at": datetime.now(timezone.utc).isoformat(),
        "health": "healthy"
    }


@app.get("/_chaos/status", summary="Current Chaos Status")
async def chaos_status():
    """Returns active chaos state on Product Service."""
    return {
        "service": "product-service",
        "active_type": chaos_state.active_type,
        "is_outage": chaos_state.is_outage,
        "latency_ms": chaos_state.latency_ms,
        "cpu_workers_active": len(chaos_state.cpu_threads) if not chaos_state.cpu_stop_event.is_set() else 0,
        "memory_allocated_mb": len(chaos_state.memory_buffer) * 10,
        "injected_at": chaos_state.injected_at
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
