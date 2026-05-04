from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_manager, get_current_active_user
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate, DriverLocationUpdate, DriverOut, DriverList
from app.repositories.driver_repository import DriverRepository
from app.utils.audit import log_action
from app.utils.helpers import paginate

router = APIRouter()


@router.get("", response_model=DriverList)
async def list_drivers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    repo = DriverRepository(db)
    skip = (page - 1) * size
    company_id = current_user.company_id if current_user.role.name != "super_admin" else None
    if company_id:
        drivers, total = await repo.get_by_company(company_id, skip=skip, limit=size)
    else:
        drivers, total = await repo.get_all(skip=skip, limit=size)
    return paginate(drivers, total, page, size)


@router.post("", response_model=DriverOut, status_code=201)
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    repo = DriverRepository(db)
    existing = await repo.get_by_user(payload.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Driver profile already exists for this user")

    driver = Driver(
        company_id=current_user.company_id,
        **payload.model_dump(),
    )
    db.add(driver)
    await db.flush()
    await db.refresh(driver)
    await log_action(db, "CREATE_DRIVER", "driver", driver.id, current_user.id)
    return driver


@router.get("/{driver_id}", response_model=DriverOut)
async def get_driver(driver_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    repo = DriverRepository(db)
    driver = await repo.get(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.put("/{driver_id}", response_model=DriverOut)
async def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    repo = DriverRepository(db)
    driver = await repo.get(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    updated = await repo.update(driver, payload.model_dump(exclude_none=True))
    await log_action(db, "UPDATE_DRIVER", "driver", driver_id, current_user.id, new_value=payload.model_dump(exclude_none=True))
    return updated


@router.put("/{driver_id}/location", response_model=DriverOut)
async def update_location(
    driver_id: int,
    payload: DriverLocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Drivers update their own GPS position."""
    repo = DriverRepository(db)
    driver = await repo.get(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    # Only the driver themselves (or admin) can update their location
    if current_user.role.name == "driver" and driver.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    from datetime import datetime, timezone
    driver.current_latitude = payload.latitude
    driver.current_longitude = payload.longitude
    driver.last_location_update = datetime.now(timezone.utc).isoformat()
    await db.flush()
    await db.refresh(driver)
    return driver
