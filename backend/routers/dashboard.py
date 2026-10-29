"""Dashboard Summary & Recovery Analysis API endpoints."""
from fastapi import APIRouter
from typing import Dict, Any, List

from backend import models
from backend.schemas import DashboardSummary, ServiceHealth
from backend.chaos.engine import chaos_engine

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary, summary="Get Dashboard Summary")
async def get_dashboard_summary():
    """Returns high-level system status, service cards, and aggregate chaos metrics."""
    # Compute overall system health
    services = chaos_engine.service_health_cache
    statuses = [s["status"] for s in services.values()]

    if any(st == "DOWN" or st == "UNHEALTHY" for st in statuses):
        overall = "UNHEALTHY"
    elif any(st == "DEGRADED" for st in statuses):
        overall = "DEGRADED"
    else:
        overall = "HEALTHY"

    history_stats = models.get_history_summary()

    active_exp = None
    if chaos_engine.active_experiment:
        # Fetch latest state from db
        active_exp = models.get_experiment_by_id(chaos_engine.active_experiment["id"]) or chaos_engine.active_experiment

    return {
        "overall_system_health": overall,
        "services": services,
        "total_experiments": history_stats["total_experiments"],
        "successful_recoveries": history_stats["successful_recoveries"],
        "failed_recoveries": history_stats["failed_recoveries"],
        "recovery_success_rate_percent": history_stats["recovery_success_rate_percent"],
        "avg_recovery_duration_ms": history_stats["avg_recovery_duration_ms"],
        "avg_detection_time_ms": history_stats["avg_detection_time_ms"],
        "avg_total_downtime_ms": history_stats["avg_total_downtime_ms"],
        "active_experiment": active_exp
    }


@router.get("/analysis", summary="Get Recovery Analysis & Comparison Data")
async def get_recovery_analysis():
    """Returns comparative recovery time statistics and trend charts."""
    history_stats = models.get_history_summary()
    recent_experiments = models.list_experiments(limit=20, status="RECOVERED")

    # Time series for charts
    chart_data = []
    for exp in reversed(recent_experiments):
        chart_data.append({
            "id": exp["id"],
            "type": exp["type"],
            "target_service": exp["target_service"],
            "start_time": exp["start_timestamp"],
            "detection_time_ms": exp.get("detection_time_ms"),
            "recovery_duration_ms": exp.get("recovery_duration_ms"),
            "total_downtime_ms": exp.get("total_downtime_ms")
        })

    # Group by experiment type
    by_type = {}
    for exp in recent_experiments:
        t = exp["type"]
        if t not in by_type:
            by_type[t] = {"count": 0, "total_recovery_ms": 0.0, "total_downtime_ms": 0.0}
        by_type[t]["count"] += 1
        if exp.get("recovery_duration_ms"):
            by_type[t]["total_recovery_ms"] += exp["recovery_duration_ms"]
        if exp.get("total_downtime_ms"):
            by_type[t]["total_downtime_ms"] += exp["total_downtime_ms"]

    type_analysis = []
    for t, vals in by_type.items():
        type_analysis.append({
            "type": t,
            "count": vals["count"],
            "avg_recovery_duration_ms": round(vals["total_recovery_ms"] / vals["count"], 2) if vals["count"] else None,
            "avg_total_downtime_ms": round(vals["total_downtime_ms"] / vals["count"], 2) if vals["count"] else None
        })

    return {
        "summary": history_stats,
        "timeline_series": chart_data,
        "type_breakdown": type_analysis
    }
