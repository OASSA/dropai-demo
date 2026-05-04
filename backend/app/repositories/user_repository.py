from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.user import User
from app.repositories.base import BaseRepository

_user_opts = [selectinload(User.role), selectinload(User.driver_profile)]


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).options(*_user_opts).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get(self, id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).options(*_user_opts).where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_company(self, company_id: int, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(User).where(User.company_id == company_id)
        )
        total = count_result.scalar()
        result = await self.db.execute(
            select(User).where(User.company_id == company_id).offset(skip).limit(limit)
        )
        return result.scalars().all(), total
