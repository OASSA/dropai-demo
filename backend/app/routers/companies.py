from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import require_super_admin, require_company_admin
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut, CompanyList
from app.utils.audit import log_action
from app.utils.helpers import paginate

router = APIRouter()


@router.get("", response_model=CompanyList)
async def list_companies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_super_admin),
):
    skip = (page - 1) * size
    count_result = await db.execute(select(func.count()).select_from(Company))
    total = count_result.scalar()
    result = await db.execute(select(Company).offset(skip).limit(size))
    companies = result.scalars().all()
    return paginate(companies, total, page, size)


@router.post("", response_model=CompanyOut, status_code=201)
async def create_company(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_super_admin),
):
    company = Company(**payload.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    await log_action(db, "CREATE_COMPANY", "company", company.id, current_user.id, new_value=payload.model_dump())
    return company


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_company_admin),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_super_admin),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old = {k: getattr(company, k) for k in payload.model_dump(exclude_none=True)}
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(company, key, value)
    await db.flush()
    await db.refresh(company)
    await log_action(db, "UPDATE_COMPANY", "company", company_id, current_user.id, old_value=old, new_value=payload.model_dump(exclude_none=True))
    return company


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_super_admin),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)
    await log_action(db, "DELETE_COMPANY", "company", company_id, current_user.id)
