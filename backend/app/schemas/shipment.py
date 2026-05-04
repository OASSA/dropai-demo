from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.shipment import ShipmentStatus, ShipmentPriority


class ShipmentCreate(BaseModel):
    origin_address: str
    origin_city: str
    origin_latitude: Optional[float] = None
    origin_longitude: Optional[float] = None
    destination_address: str
    destination_city: str
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
    recipient_name: str
    recipient_phone: str
    recipient_email: Optional[str] = None
    weight_kg: Optional[float] = None
    dimensions: Optional[str] = None
    description: Optional[str] = None
    declared_value: Optional[float] = None
    is_fragile: bool = False
    priority: ShipmentPriority = ShipmentPriority.normal
    origin_warehouse_id: Optional[int] = None
    destination_warehouse_id: Optional[int] = None
    scheduled_pickup: Optional[datetime] = None
    scheduled_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentAssign(BaseModel):
    driver_id: int


class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatus
    message: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_address: Optional[str] = None


class TrackingLogOut(BaseModel):
    id: int
    status: ShipmentStatus
    message: Optional[str] = None
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ShipmentOut(BaseModel):
    id: int
    tracking_number: str
    status: ShipmentStatus
    priority: ShipmentPriority
    company_id: int
    origin_address: str
    origin_city: str
    destination_address: str
    destination_city: str
    recipient_name: str
    recipient_phone: str
    recipient_email: Optional[str] = None
    weight_kg: Optional[float] = None
    is_fragile: bool
    driver_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    scheduled_pickup: Optional[datetime] = None
    actual_pickup: Optional[datetime] = None
    scheduled_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    predicted_eta: Optional[datetime] = None
    predicted_distance_km: Optional[float] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShipmentDetail(ShipmentOut):
    tracking_logs: list[TrackingLogOut] = []

    class Config:
        from_attributes = True


class ShipmentList(BaseModel):
    items: list[ShipmentOut]
    total: int
    page: int
    size: int


class PublicTrackingOut(BaseModel):
    tracking_number: str
    status: ShipmentStatus
    origin_city: str
    destination_city: str
    recipient_name: str
    predicted_eta: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    tracking_logs: list[TrackingLogOut] = []

    class Config:
        from_attributes = True
