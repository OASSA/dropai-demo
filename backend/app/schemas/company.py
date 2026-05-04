from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    subscription_plan: str = "basic"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_plan: Optional[str] = None


class CompanyOut(CompanyBase):
    id: int
    logo_url: Optional[str] = None
    is_active: bool
    subscription_plan: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyList(BaseModel):
    items: list[CompanyOut]
    total: int
    page: int
    size: int
