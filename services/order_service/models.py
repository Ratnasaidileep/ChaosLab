"""Data models for Order Service."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity of items")


class CreateOrderRequest(BaseModel):
    customer_name: str
    customer_email: str
    items: List[OrderItem]


class Order(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    status: str
    total_amount: float
    items: List[dict]
    created_at: str


class ChaosInjectionRequest(BaseModel):
    type: str  # dependency_failure, outage, cpu, memory, latency
    duration_seconds: int = 15
    load_percent: Optional[int] = 70
    memory_mb: Optional[int] = 150
    delay_ms: Optional[int] = 1000
    target_dependency: Optional[str] = "product-service"
