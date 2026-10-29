"""Database layer for Order Service using SQLite."""
import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

DB_FILE = os.getenv("ORDER_DB_PATH", "orders.db")

INITIAL_SAMPLE_ORDERS = [
    (1, "ORD-7001", "Alice Smith", "alice@example.com", "COMPLETED", 1499.99, json.dumps([{"product_id": 1, "product_name": "Laptop Pro 15", "quantity": 1, "price": 1499.99}]), "2026-10-28T10:00:00Z"),
    (2, "ORD-7002", "Bob Johnson", "bob@example.com", "COMPLETED", 169.49, json.dumps([{"product_id": 2, "product_name": "Wireless Mechanical Keyboard", "quantity": 1, "price": 119.50}, {"product_id": 3, "product_name": "Ergonomic Precision Mouse", "quantity": 1, "price": 49.99}]), "2026-10-28T11:30:00Z"),
]


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize orders table and sample data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            items_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany("""
            INSERT INTO orders (id, order_number, customer_name, customer_email, status, total_amount, items_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, INITIAL_SAMPLE_ORDERS)
        conn.commit()
    conn.close()


def list_orders() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_number, customer_name, customer_email, status, total_amount, items_json, created_at FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["items"] = json.loads(d.pop("items_json"))
        result.append(d)
    return result


def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_number, customer_name, customer_email, status, total_amount, items_json, created_at FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["items"] = json.loads(d.pop("items_json"))
    return d


def create_order(customer_name: str, customer_email: str, items: List[Dict[str, Any]], total_amount: float) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    order_number = f"ORD-{int(datetime.now().timestamp() * 1000) % 1000000:06d}"
    items_json = json.dumps(items)

    cursor.execute("""
        INSERT INTO orders (order_number, customer_name, customer_email, status, total_amount, items_json, created_at)
        VALUES (?, ?, ?, 'CONFIRMED', ?, ?, ?)
    """, (order_number, customer_name, customer_email, total_amount, items_json, now_iso))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    return {
        "id": order_id,
        "order_number": order_number,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "status": "CONFIRMED",
        "total_amount": total_amount,
        "items": items,
        "created_at": now_iso
    }
