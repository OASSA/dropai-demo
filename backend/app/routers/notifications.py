from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.notification import Notification
from app.utils.helpers import paginate
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationOut(BaseModel):
    id: int
    type: str
    channel: str
    title: str
    message: str
    is_read: bool
    shipment_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("", response_model=dict)
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    skip = (page - 1) * size
    filters = [Notification.user_id == current_user.id]
    if unread_only:
        filters.append(Notification.is_read == False)

    from sqlalchemy import and_
    total = (await db.execute(select(func.count()).select_from(Notification).where(and_(*filters)))).scalar()
    result = await db.execute(
        select(Notification).where(and_(*filters)).order_by(Notification.created_at.desc()).offset(skip).limit(size)
    )
    notifs = result.scalars().all()
    return paginate([NotificationOut.model_validate(n) for n in notifs], total, page, size)


@router.put("/{notif_id}/read", status_code=200)
async def mark_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
    return {"success": True}


@router.put("/mark-all-read", status_code=200)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
    )
    for notif in result.scalars().all():
        notif.is_read = True
    return {"success": True}
