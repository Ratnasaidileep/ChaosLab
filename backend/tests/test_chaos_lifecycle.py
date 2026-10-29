"""Lifecycle and recovery controller tests for Chaos Engine."""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from backend.chaos.engine import ChaosEngine
from backend import models


@pytest.fixture(autouse=True)
def init_db():
    models.init_db()
    yield


@pytest.mark.asyncio
async def test_chaos_engine_lifecycle_mocked():
    engine = ChaosEngine()

    with patch("backend.chaos.engine.inject_failure", new_callable=AsyncMock) as mock_inject, \
         patch("backend.chaos.engine.execute_recovery_action", new_callable=AsyncMock) as mock_rec, \
         patch("backend.chaos.engine.verify_service_health", new_callable=AsyncMock) as mock_verify, \
         patch.object(engine, "probe_is_failed", new_callable=AsyncMock) as mock_probe:

        mock_inject.return_value = {"mode": "http_simulation"}
        mock_rec.return_value = {"status": "recovered"}
        mock_verify.return_value = (True, {"status": "healthy"})
        mock_probe.return_value = True

        exp = engine.start_experiment(
            exp_type="cpu_stress",
            target_service="product-service",
            params={"duration_seconds": 1, "load_percent": 50}
        )
        assert exp["id"].startswith("exp-")
        assert engine.active_experiment is not None

        # Wait for background task to complete (duration is 1s)
        await asyncio.sleep(2.0)

        # Check saved experiment in database
        saved = models.get_experiment_by_id(exp["id"])
        assert saved is not None
        assert saved["status"] == "RECOVERED"
        assert saved["recovery_outcome"] == "SUCCESS"
        assert saved["recovery_duration_ms"] is not None
        assert saved["total_downtime_ms"] is not None
        assert engine.active_experiment is None


@pytest.mark.asyncio
async def test_chaos_engine_cancellation():
    engine = ChaosEngine()

    with patch("backend.chaos.engine.inject_failure", new_callable=AsyncMock) as mock_inject, \
         patch("backend.chaos.engine.execute_recovery_action", new_callable=AsyncMock) as mock_rec, \
         patch.object(engine, "probe_is_failed", new_callable=AsyncMock) as mock_probe:

        mock_inject.return_value = {"mode": "http_simulation"}
        mock_rec.return_value = {"status": "recovered"}
        mock_probe.return_value = True

        exp = engine.start_experiment(
            exp_type="cpu_stress",
            target_service="order-service",
            params={"duration_seconds": 20, "load_percent": 50}
        )

        await asyncio.sleep(0.3)
        cancelled = engine.cancel_active_experiment(exp["id"])
        assert cancelled is True

        await asyncio.sleep(0.8)
        saved = models.get_experiment_by_id(exp["id"])
        assert saved["status"] == "CANCELLED"
        assert saved["recovery_outcome"] == "CANCELLED_BY_USER"
