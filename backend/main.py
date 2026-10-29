"""ChaosLab Control Plane Backend API.

FastAPI orchestration service for controlled chaos injection, automated recovery,
Prometheus monitoring metrics, and experiment telemetry.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

from backend.config import settings
from backend import models
from backend.routers import dashboard, services, experiments
from backend.chaos.engine import chaos_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chaoslab.main")

# Prometheus Metrics for ChaosLab Control Plane
CHAOS_EXPERIMENTS_TOTAL = Counter(
    "chaoslab_experiments_total",
    "Total chaos experiments triggered",
    ["type", "target_service"]
)
CHAOS_RECOVERIES_TOTAL = Counter(
    "chaoslab_recoveries_total",
    "Total chaos recoveries completed",
    ["outcome"]
)
SYSTEM_HEALTH_GAUGE = Gauge(
    "chaoslab_system_health",
    "System overall resilience status (2=Healthy, 1=Degraded, 0=Unhealthy)"
)


async def _background_health_poller():
    """Continuously polls target services to provide real-time telemetry."""
    while True:
        try:
            await chaos_engine.poll_service_health()
            # Update system health gauge
            statuses = [s["status"] for s in chaos_engine.service_health_cache.values()]
            if any(st == "DOWN" or st == "UNHEALTHY" for st in statuses):
                SYSTEM_HEALTH_GAUGE.set(0)
            elif any(st == "DEGRADED" for st in statuses):
                SYSTEM_HEALTH_GAUGE.set(1)
            else:
                SYSTEM_HEALTH_GAUGE.set(2)
        except Exception as e:
            logger.debug(f"Health poller tick error: {e}")
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing ChaosLab database...")
    models.init_db()
    poller_task = asyncio.create_task(_background_health_poller())
    logger.info("ChaosLab Control Plane initialized.")
    yield
    # Shutdown
    poller_task.cancel()
    logger.info("ChaosLab Control Plane shutdown completed.")


app = FastAPI(
    title="ChaosLab API",
    description="Automated Failure Injection & Resilience Recovery Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Routers
app.include_router(dashboard.router)
app.include_router(services.router)
app.include_router(experiments.router)


@app.get("/health", summary="Health Check for ChaosLab API")
async def health_check():
    """ChaosLab control plane health status."""
    return {
        "status": "healthy",
        "service": "chaoslab-backend",
        "environment": settings.CHAOSLAB_ENV,
        "active_experiment": chaos_engine.active_experiment is not None
    }


@app.get("/metrics", summary="Prometheus Metrics")
async def metrics():
    """Prometheus telemetry scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.CHAOSLAB_HOST, port=settings.CHAOSLAB_PORT, reload=False)
