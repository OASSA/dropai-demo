from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.shipment import Shipment, ShipmentStatus
from app.repositories.base import BaseRepository

_detail_opts = [selectinload(Shipment.tracking_logs), selectinload(Shipment.driver)]


class ShipmentRepository(BaseRepository[Shipment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Shipment, db)

    async def get_by_tracking(self, tracking_number: str) -> Optional[Shipment]:
        result = await self.db.execute(
            select(Shipment)
            .options(*_detail_opts)
            .where(Shipment.tracking_number == tracking_number)
        )
        return result.scalar_one_or_none()

    async def get(self, id: int) -> Optional[Shipment]:
        result = await self.db.execute(
            select(Shipment)
            .options(*_detail_opts)
            .where(Shipment.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_company(
        self,
        company_id: Optional[int],
        skip: int = 0,
        limit: int = 20,
        status: Optional[ShipmentStatus] = None,
    ) -> tuple[List[Shipment], int]:
        filters = []
        if company_id is not None:
            filters.append(Shipment.company_id == company_id)
        if status:
            filters.append(Shipment.status == status)

        count_result = await self.db.execute(
            select(func.count()).select_from(Shipment).where(and_(*filters))
        )
        total = count_result.scalar()
        result = await self.db.execute(
            select(Shipment)
            .where(and_(*filters))
            .order_by(Shipment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all(), total

    async def get_by_driver(self, driver_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Shipment], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(Shipment).where(Shipment.driver_id == driver_id)
        )
        total = count_result.scalar()
        result = await self.db.execute(
            select(Shipment)
            .where(Shipment.driver_id == driver_id)
            .order_by(Shipment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all(), total

    async def count_by_status(self, company_id: Optional[int] = None) -> dict:
        filters = []
        if company_id:
            filters.append(Shipment.company_id == company_id)

        counts = {}
        for status in ShipmentStatus:
            status_filters = filters + [Shipment.status == status]
            result = await self.db.execute(
                select(func.count()).select_from(Shipment).where(and_(*status_filters))
            )
            counts[status.value] = result.scalar()
        return counts
