"""Database layer for Product Service using SQLite."""
import sqlite3
import os
from typing import List, Optional, Dict, Any

DB_FILE = os.getenv("PRODUCT_DB_PATH", "products.db")

SAMPLE_PRODUCTS = [
    (1, "Laptop Pro 15", "High-performance developer laptop with 32GB RAM and 1TB SSD", 1499.99, 25, "Electronics"),
    (2, "Wireless Mechanical Keyboard", "Low-profile tactile mechanical keyboard with RGB backlighting", 119.50, 60, "Accessories"),
    (3, "Ergonomic Precision Mouse", "Precision Bluetooth mouse with customizable thumb buttons", 49.99, 120, "Accessories"),
    (4, "UltraWide 34-Inch Curved Monitor", "WQHD 144Hz display with HDR400 and USB-C hub connectivity", 489.00, 18, "Electronics"),
    (5, "Noise-Cancelling Headphones", "Over-ear active noise-cancelling headphones with 40h battery", 199.95, 45, "Audio"),
    (6, "USB-C Multiport Adapter", "7-in-1 hub with 4K HDMI, SD card reader, and 100W Power Delivery", 39.99, 85, "Accessories")
]


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize products table and seed data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany("""
            INSERT INTO products (id, name, description, price, stock, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, SAMPLE_PRODUCTS)
        conn.commit()
    conn.close()


def list_products() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, stock, category FROM products ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, stock, category FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def reserve_stock(product_id: int, quantity: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"reserved": False, "remaining_stock": 0, "message": f"Product {product_id} not found"}

    current_stock = row[0]
    if current_stock < quantity:
        conn.close()
        return {"reserved": False, "remaining_stock": current_stock, "message": f"Insufficient stock. Requested: {quantity}, Available: {current_stock}"}

    new_stock = current_stock - quantity
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()
    return {"reserved": True, "remaining_stock": new_stock, "message": f"Successfully reserved {quantity} units"}


def release_stock(product_id: int, quantity: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
    conn.commit()
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    remaining = row[0] if row else 0
    return {"reserved": False, "remaining_stock": remaining, "message": f"Released {quantity} units"}
