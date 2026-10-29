"""Unit tests for experiment metric calculations (Requirement 8)."""
import pytest
from datetime import datetime, timezone, timedelta
from backend.chaos.engine import calculate_metrics, parse_iso


def test_parse_iso():
    iso_str = "2026-10-28T12:00:00+00:00"
    dt = parse_iso(iso_str)
    assert dt is not None
    assert dt.year == 2026

    # None or invalid returns None
    assert parse_iso(None) is None
    assert parse_iso("not-a-date") is None


def test_calculate_metrics_complete():
    t0 = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
    failure_ts = t0.isoformat()
    detection_ts = (t0 + timedelta(seconds=1.5)).isoformat()
    recovery_start_ts = (t0 + timedelta(seconds=15.0)).isoformat()
    recovery_ts = (t0 + timedelta(seconds=18.25)).isoformat()

    metrics = calculate_metrics(failure_ts, detection_ts, recovery_start_ts, recovery_ts)

    # Detection time: 1.5s = 1500.0ms
    assert metrics["detection_time_ms"] == 1500.0
    # Recovery duration: 18.25s - 15.0s = 3.25s = 3250.0ms
    assert metrics["recovery_duration_ms"] == 3250.0
    # Total downtime: 18.25s - 0s = 18.25s = 18250.0ms
    assert metrics["total_downtime_ms"] == 18250.0


def test_calculate_metrics_missing_recovery():
    """If recovery does not occur, metrics must be None, never fabricated."""
    t0 = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
    failure_ts = t0.isoformat()
    detection_ts = (t0 + timedelta(seconds=2.0)).isoformat()

    metrics = calculate_metrics(failure_ts, detection_ts, None, None)

    assert metrics["detection_time_ms"] == 2000.0
    assert metrics["recovery_duration_ms"] is None
    assert metrics["total_downtime_ms"] is None


def test_calculate_metrics_all_none():
    metrics = calculate_metrics(None, None, None, None)
    assert metrics["detection_time_ms"] is None
    assert metrics["recovery_duration_ms"] is None
    assert metrics["total_downtime_ms"] is None
