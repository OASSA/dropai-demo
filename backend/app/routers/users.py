from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import require_company_admin, get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserList
from app.repositories.user_repository import UserRepository
from app.utils.audit import log_action
from app.utils.helpers import paginate

router = APIRouter()


@router.get("", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_company_admin),
):
    repo = UserRepository(db)
    skip = (page - 1) * size
    # Super admin sees all; company admin sees own company
    if current_user.role.name == "super_admin":
        users, total = await repo.get_all(skip=skip, limit=size)
    else:
        users, total = await repo.get_by_company(current_user.company_id, skip=skip, limit=size)
    return paginate(users, total, page, size)


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_company_admin),
):
    repo = UserRepository(db)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(Role).where(Role.id == payload.role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        role_id=payload.role_id,
        company_id=payload.company_id or current_user.company_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    await log_action(db, "CREATE_USER", "user", user.id, current_user.id, new_value={"email": user.email, "role_id": user.role_id})
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Users can view own profile; admins can view any
    if current_user.id != user_id and current_user.role.name not in ("super_admin", "company_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user_id and current_user.role.name not in ("super_admin", "company_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    old = payload.model_dump(exclude_none=True)
    updated = await repo.update(user, payload.model_dump(exclude_none=True))
    await log_action(db, "UPDATE_USER", "user", user_id, current_user.id, old_value=old, new_value=payload.model_dump(exclude_none=True))
    return updated


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_company_admin),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.delete(user)
    await log_action(db, "DELETE_USER", "user", user_id, current_user.id)
