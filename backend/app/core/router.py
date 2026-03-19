import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import AuditLog
from app.core.schemas import AuditLogResponse, FiscalYearCreate, FiscalYearResponse, PeriodResponse
from app.core.service import create_fiscal_year, get_fiscal_year, list_fiscal_years, lock_period
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/core", tags=["core"])


@router.get("/fiscal-years", response_model=list[FiscalYearResponse])
async def get_fiscal_years(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_fiscal_years(db, current_user["tenant_id"], dossier_id)


@router.post("/fiscal-years", response_model=FiscalYearResponse, status_code=201)
async def post_fiscal_year(
    data: FiscalYearCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_fiscal_year(db, current_user["tenant_id"], data)


@router.get("/fiscal-years/{fy_id}", response_model=FiscalYearResponse)
async def get_fiscal_year_detail(
    fy_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_fiscal_year(db, current_user["tenant_id"], fy_id)


@router.get("/fiscal-years/{fy_id}/periods", response_model=list[PeriodResponse])
async def get_periods(
    fy_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fy = await get_fiscal_year(db, current_user["tenant_id"], fy_id)
    return fy.periods


@router.post("/periods/{period_id}/lock", response_model=PeriodResponse)
async def post_lock_period(
    period_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await lock_period(db, current_user["tenant_id"], period_id)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = Query(default=50, le=200),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).where(
        AuditLog.tenant_id == current_user["tenant_id"]
    )
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    query = query.order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())
