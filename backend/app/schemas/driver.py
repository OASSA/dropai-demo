from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.driver import DriverStatus, VehicleType


class DriverCreate(BaseModel):
    user_id: int
    license_number: str
    vehicle_type: VehicleType
    vehicle_plate: str
    vehicle_model: Optional[str] = None
    notes: Optional[str] = None


class DriverUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    vehicle_plate: Optional[str] = None
    vehicle_model: Optional[str] = None
    status: Optional[DriverStatus] = None
    notes: Optional[str] = None


class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float


class DriverOut(BaseModel):
    id: int
    user_id: int
    company_id: int
    license_number: str
    vehicle_type: VehicleType
    vehicle_plate: str
    vehicle_model: Optional[str] = None
    status: DriverStatus
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    performance_score: float
    total_deliveries: int
    successful_deliveries: int
    average_rating: float
    success_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DriverList(BaseModel):
    items: list[DriverOut]
    total: int
    page: int
    size: int
