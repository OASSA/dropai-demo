from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import require_manager, get_current_active_user
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseOut, WarehouseList
from app.utils.audit import log_action
from app.utils.helpers import paginate, generate_warehouse_code

router = APIRouter()


@router.get("", response_model=WarehouseList)
async def list_warehouses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    skip = (page - 1) * size
    filters = [] if current_user.role.name == "super_admin" else [Warehouse.company_id == current_user.company_id]
    from sqlalchemy import and_
    count_result = await db.execute(select(func.count()).select_from(Warehouse).where(and_(*filters)))
    total = count_result.scalar()
    result = await db.execute(select(Warehouse).where(and_(*filters)).offset(skip).limit(size))
    return paginate(result.scalars().all(), total, page, size)


@router.post("", response_model=WarehouseOut, status_code=201)
async def create_warehouse(
    payload: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    code = payload.code or generate_warehouse_code(payload.name)
    warehouse = Warehouse(
        company_id=current_user.company_id,
        code=code,
        **{k: v for k, v in payload.model_dump().items() if k != "code"},
    )
    db.add(warehouse)
    await db.flush()
    await db.refresh(warehouse)
    await log_action(db, "CREATE_WAREHOUSE", "warehouse", warehouse.id, current_user.id)
    return warehouse


@router.get("/{warehouse_id}", response_model=WarehouseOut)
async def get_warehouse(warehouse_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseOut)
async def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(warehouse, k, v)
    await db.flush()
    await db.refresh(warehouse)
    await log_action(db, "UPDATE_WAREHOUSE", "warehouse", warehouse_id, current_user.id)
    return warehouse


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    await db.delete(warehouse)
    await log_action(db, "DELETE_WAREHOUSE", "warehouse", warehouse_id, current_user.id)
