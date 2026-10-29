"""Database access and persistent history for ChaosLab."""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from backend.config import settings


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(settings.DB_PATH) if os.path.dirname(settings.DB_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize experiments and audit tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            target_service TEXT NOT NULL,
            parameters TEXT NOT NULL,
            status TEXT NOT NULL,
            start_timestamp TEXT NOT NULL,
            failure_timestamp TEXT,
            detection_timestamp TEXT,
            recovery_start_timestamp TEXT,
            recovery_timestamp TEXT,
            detection_time_ms REAL,
            recovery_duration_ms REAL,
            total_downtime_ms REAL,
            recovery_outcome TEXT,
            error_details TEXT,
            logs TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            product_service_status TEXT NOT NULL,
            order_service_status TEXT NOT NULL,
            system_status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_experiment(exp: Dict[str, Any]) -> None:
    """Insert or update an experiment record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO experiments (
            id, type, target_service, parameters, status,
            start_timestamp, failure_timestamp, detection_timestamp,
            recovery_start_timestamp, recovery_timestamp,
            detection_time_ms, recovery_duration_ms, total_downtime_ms,
            recovery_outcome, error_details, logs
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exp["id"],
        exp["type"],
        exp["target_service"],
        json.dumps(exp.get("parameters", {})),
        exp["status"],
        exp.get("start_timestamp"),
        exp.get("failure_timestamp"),
        exp.get("detection_timestamp"),
        exp.get("recovery_start_timestamp"),
        exp.get("recovery_timestamp"),
        exp.get("detection_time_ms"),
        exp.get("recovery_duration_ms"),
        exp.get("total_downtime_ms"),
        exp.get("recovery_outcome"),
        exp.get("error_details"),
        json.dumps(exp.get("logs", []))
    ))
    conn.commit()
    conn.close()


def get_experiment_by_id(exp_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["parameters"] = json.loads(d["parameters"]) if d["parameters"] else {}
    d["logs"] = json.loads(d["logs"]) if d["logs"] else []
    return d


def list_experiments(
    limit: int = 50,
    offset: int = 0,
    exp_type: Optional[str] = None,
    target_service: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM experiments WHERE 1=1"
    params: list = []

    if exp_type:
        query += " AND type = ?"
        params.append(exp_type)
    if target_service:
        query += " AND target_service = ?"
        params.append(target_service)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY start_timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        d = dict(row)
        d["parameters"] = json.loads(d["parameters"]) if d["parameters"] else {}
        d["logs"] = json.loads(d["logs"]) if d["logs"] else []
        result.append(d)
    return result


def get_history_summary() -> Dict[str, Any]:
    """Calculate aggregate recovery metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'RECOVERED'")
    successful_recoveries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'FAILED'")
    failed_recoveries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'CANCELLED'")
    cancelled = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(recovery_duration_ms), AVG(detection_time_ms), AVG(total_downtime_ms) FROM experiments WHERE status = 'RECOVERED'")
    avg_rec, avg_det, avg_down = cursor.fetchone()

    conn.close()

    success_rate = round((successful_recoveries / total_experiments) * 100, 1) if total_experiments > 0 else 0.0

    return {
        "total_experiments": total_experiments,
        "successful_recoveries": successful_recoveries,
        "failed_recoveries": failed_recoveries,
        "cancelled_experiments": cancelled,
        "recovery_success_rate_percent": success_rate,
        "avg_recovery_duration_ms": round(avg_rec, 2) if avg_rec else None,
        "avg_detection_time_ms": round(avg_det, 2) if avg_det else None,
        "avg_total_downtime_ms": round(avg_down, 2) if avg_down else None,
    }
