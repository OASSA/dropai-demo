from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShipmentStats(BaseModel):
    total: int
    pending: int
    in_transit: int
    delivered: int
    failed: int
    cancelled: int
    delivery_success_rate: float


class DriverStats(BaseModel):
    total_drivers: int
    available: int
    on_delivery: int
    off_duty: int
    top_performer_name: Optional[str] = None
    top_performer_score: Optional[float] = None


class DeliveryTrendPoint(BaseModel):
    date: str
    delivered: int
    failed: int
    total: int


class CompanyStats(BaseModel):
    total_companies: int
    active_companies: int
    new_this_month: int


class DashboardStats(BaseModel):
    shipments: ShipmentStats
    drivers: DriverStats
    companies: Optional[CompanyStats] = None
    delivery_trend: list[DeliveryTrendPoint] = []
    avg_delivery_time_hours: Optional[float] = None
    total_distance_km: Optional[float] = None


class RecentActivity(BaseModel):
    id: int
    action: str
    description: str
    timestamp: datetime
    user_name: Optional[str] = None
