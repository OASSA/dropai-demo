from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    manager_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    capacity: Optional[int] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_id: Optional[int] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class WarehouseOut(BaseModel):
    id: int
    company_id: int
    name: str
    code: str
    address: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    manager_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    capacity: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WarehouseList(BaseModel):
    items: list[WarehouseOut]
    total: int
    page: int
    size: int
