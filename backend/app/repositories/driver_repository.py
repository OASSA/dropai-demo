from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.models.driver import Driver, DriverStatus
from app.repositories.base import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    def __init__(self, db: AsyncSession):
        super().__init__(Driver, db)

    async def get_by_user(self, user_id: int) -> Optional[Driver]:
        result = await self.db.execute(select(Driver).where(Driver.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_available_by_company(self, company_id: int) -> List[Driver]:
        result = await self.db.execute(
            select(Driver).where(
                Driver.company_id == company_id,
                Driver.status == DriverStatus.available,
            ).order_by(Driver.performance_score.desc())
        )
        return result.scalars().all()

    async def get_by_company(self, company_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Driver], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(Driver).where(Driver.company_id == company_id)
        )
        total = count_result.scalar()
        result = await self.db.execute(
            select(Driver).where(Driver.company_id == company_id).offset(skip).limit(limit)
        )
        return result.scalars().all(), total
