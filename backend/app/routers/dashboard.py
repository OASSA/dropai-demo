from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.shipment import Shipment, ShipmentStatus
from app.models.driver import Driver, DriverStatus
from app.models.company import Company
from app.models.audit_log import AuditLog
from app.schemas.dashboard import DashboardStats, ShipmentStats, DriverStats, CompanyStats, DeliveryTrendPoint, RecentActivity

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    company_id = None if current_user.role.name == "super_admin" else current_user.company_id
    ship_filter = [] if not company_id else [Shipment.company_id == company_id]
    drv_filter = [] if not company_id else [Driver.company_id == company_id]

    # Shipment stats
    status_counts = {}
    for s in ShipmentStatus:
        result = await db.execute(
            select(func.count()).select_from(Shipment).where(and_(*ship_filter, Shipment.status == s))
        )
        status_counts[s.value] = result.scalar()

    total_shipments = sum(status_counts.values())
    delivered = status_counts.get("delivered", 0)
    failed = status_counts.get("failed", 0)
    success_rate = round((delivered / total_shipments * 100) if total_shipments > 0 else 0, 1)

    shipment_stats = ShipmentStats(
        total=total_shipments,
        pending=status_counts.get("pending", 0),
        in_transit=status_counts.get("in_transit", 0),
        delivered=delivered,
        failed=failed,
        cancelled=status_counts.get("cancelled", 0),
        delivery_success_rate=success_rate,
    )

    # Driver stats
    drv_counts = {}
    for s in DriverStatus:
        result = await db.execute(
            select(func.count()).select_from(Driver).where(and_(*drv_filter, Driver.status == s))
        )
        drv_counts[s.value] = result.scalar()

    top_driver = None
    top_score = None
    top_result = await db.execute(
        select(Driver).where(and_(*drv_filter)).order_by(Driver.performance_score.desc()).limit(1)
    )
    top = top_result.scalar_one_or_none()
    if top:
        top_driver = top.user.full_name if top.user else str(top.id)
        top_score = top.performance_score

    driver_stats = DriverStats(
        total_drivers=sum(drv_counts.values()),
        available=drv_counts.get("available", 0),
        on_delivery=drv_counts.get("on_delivery", 0),
        off_duty=drv_counts.get("off_duty", 0),
        top_performer_name=top_driver,
        top_performer_score=top_score,
    )

    # Company stats (super admin only)
    company_stats = None
    if current_user.role.name == "super_admin":
        total_co = (await db.execute(select(func.count()).select_from(Company))).scalar()
        active_co = (await db.execute(select(func.count()).select_from(Company).where(Company.is_active == True))).scalar()
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0)
        new_co = (await db.execute(select(func.count()).select_from(Company).where(Company.created_at >= month_start))).scalar()
        company_stats = CompanyStats(total_companies=total_co, active_companies=active_co, new_this_month=new_co)

    # 30-day delivery trend
    trend = []
    for i in range(29, -1, -1):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        filters_day = ship_filter + [Shipment.created_at >= day_start, Shipment.created_at < day_end]
        total_day = (await db.execute(select(func.count()).select_from(Shipment).where(and_(*filters_day)))).scalar()
        del_day = (await db.execute(select(func.count()).select_from(Shipment).where(and_(*filters_day, Shipment.status == ShipmentStatus.delivered)))).scalar()
        fail_day = (await db.execute(select(func.count()).select_from(Shipment).where(and_(*filters_day, Shipment.status == ShipmentStatus.failed)))).scalar()
        trend.append(DeliveryTrendPoint(date=day.strftime("%Y-%m-%d"), delivered=del_day, failed=fail_day, total=total_day))

    return DashboardStats(
        shipments=shipment_stats,
        drivers=driver_stats,
        companies=company_stats,
        delivery_trend=trend,
    )


@router.get("/activity", response_model=list[RecentActivity])
async def recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        RecentActivity(
            id=log.id,
            action=log.action,
            description=log.description or f"{log.action} on {log.resource_type} #{log.resource_id}",
            timestamp=log.created_at,
            user_name=log.user.full_name if log.user else "System",
        )
        for log in logs
    ]
