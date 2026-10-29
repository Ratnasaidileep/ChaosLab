"""Data models for Product Service."""
from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str


class StockReservationRequest(BaseModel):
    quantity: int = Field(gt=0, description="Quantity to reserve")


class StockReservationResponse(BaseModel):
    product_id: int
    reserved: bool
    remaining_stock: int
    message: str


class ChaosInjectionRequest(BaseModel):
    type: str  # cpu, memory, outage, latency
    duration_seconds: int = 15
    load_percent: Optional[int] = 70
    memory_mb: Optional[int] = 150
    delay_ms: Optional[int] = 1000
