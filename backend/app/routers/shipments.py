from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_manager
from app.models.shipment import ShipmentStatus
from app.schemas.shipment import (
    ShipmentCreate, ShipmentAssign, ShipmentStatusUpdate,
    ShipmentOut, ShipmentDetail, ShipmentList, PublicTrackingOut
)
from app.repositories.shipment_repository import ShipmentRepository
from app.services.shipment_service import shipment_service
from app.utils.helpers import paginate

router = APIRouter()


@router.post("", response_model=ShipmentOut, status_code=201)
async def create_shipment(
    payload: ShipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    return await shipment_service.create(db, payload, current_user.company_id, current_user.id)


@router.get("", response_model=ShipmentList)
async def list_shipments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[ShipmentStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    repo = ShipmentRepository(db)
    skip = (page - 1) * size
    # Drivers only see their own shipments
    if current_user.role.name == "driver" and current_user.driver_profile:
        shipments, total = await repo.get_by_driver(current_user.driver_profile.id, skip=skip, limit=size)
    else:
        company_id = None if current_user.role.name == "super_admin" else current_user.company_id
        shipments, total = await repo.get_by_company(company_id, skip=skip, limit=size, status=status)
    return paginate(shipments, total, page, size)


@router.get("/track/{tracking_number}", response_model=PublicTrackingOut)
async def public_tracking(tracking_number: str, db: AsyncSession = Depends(get_db)):
    """Public endpoint — no auth required. Exposes only safe fields."""
    repo = ShipmentRepository(db)
    shipment = await repo.get_by_tracking(tracking_number)
    if not shipment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentDetail)
async def get_shipment(
    shipment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    repo = ShipmentRepository(db)
    shipment = await repo.get(shipment_id)
    if not shipment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}/assign", response_model=ShipmentOut)
async def assign_driver(
    shipment_id: int,
    payload: ShipmentAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    return await shipment_service.assign_driver(db, shipment_id, payload, current_user.id)


@router.put("/{shipment_id}/status", response_model=ShipmentOut)
async def update_status(
    shipment_id: int,
    payload: ShipmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return await shipment_service.update_status(db, shipment_id, payload, current_user.id)
