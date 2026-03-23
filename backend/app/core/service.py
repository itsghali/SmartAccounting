import uuid
from calendar import monthrange
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models import AccountingPeriod, AuditLog, FiscalYear
from app.core.schemas import FiscalYearCreate
from app.shared.dates import ensure_not_past_business_date
from app.shared.exceptions import BadRequestError, NotFoundError
from app.tenant.models import Dossier


async def _ensure_dossier_exists(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> Dossier:
    result = await db.execute(
        select(Dossier).where(
            Dossier.id == dossier_id,
            Dossier.tenant_id == tenant_id,
            Dossier.status != "deleted",
        )
    )
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise NotFoundError("Dossier not found or no longer accessible")
    return dossier


async def create_fiscal_year(
    db: AsyncSession, tenant_id: uuid.UUID, data: FiscalYearCreate
) -> FiscalYear:
    await _ensure_dossier_exists(db, tenant_id, data.dossier_id)
    ensure_not_past_business_date(data.start_date, "date de debut")
    ensure_not_past_business_date(data.end_date, "date de fin")

    if data.end_date <= data.start_date:
        raise BadRequestError(
            "La date de fin doit etre posterieure a la date de debut"
        )

    delta_months = (data.end_date.year - data.start_date.year) * 12 + (
        data.end_date.month - data.start_date.month
    )
    if delta_months > 18:
        raise BadRequestError(
            "Un exercice ne peut pas depasser 18 mois"
        )

    existing = await db.execute(
        select(FiscalYear).where(
            FiscalYear.dossier_id == data.dossier_id,
            FiscalYear.status.in_(["CREATED", "OPEN"]),
            FiscalYear.tenant_id == tenant_id,
        )
    )
    existing_fiscal_year = existing.scalar_one_or_none()
    if existing_fiscal_year:
        raise BadRequestError(
            f"Un exercice est deja ouvert sur ce dossier : "
            f"{existing_fiscal_year.name} "
            f"({existing_fiscal_year.start_date} -> {existing_fiscal_year.end_date}). "
            "Fermez ou reouvrez le workflow de cloture avant d'en creer un nouveau."
        )

    overlap = await db.execute(
        select(FiscalYear).where(
            FiscalYear.dossier_id == data.dossier_id,
            FiscalYear.tenant_id == tenant_id,
            FiscalYear.start_date <= data.end_date,
            FiscalYear.end_date >= data.start_date,
        )
    )
    overlapping_fiscal_year = overlap.scalar_one_or_none()
    if overlapping_fiscal_year:
        raise BadRequestError(
            f"Les dates proposees chevauchent l'exercice existant "
            f"{overlapping_fiscal_year.name} "
            f"({overlapping_fiscal_year.start_date} -> {overlapping_fiscal_year.end_date})"
        )

    fy = FiscalYear(
        tenant_id=tenant_id,
        dossier_id=data.dossier_id,
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        status="OPEN",
    )
    db.add(fy)
    await db.flush()

    # Generate monthly periods
    current = data.start_date
    period_num = 1
    while current < data.end_date:
        _, last_day = monthrange(current.year, current.month)
        period_end = date(current.year, current.month, last_day)
        if period_end > data.end_date:
            period_end = data.end_date

        period = AccountingPeriod(
            tenant_id=tenant_id,
            fiscal_year_id=fy.id,
            dossier_id=data.dossier_id,
            name=f"{current.strftime('%m/%Y')}",
            start_date=current,
            end_date=period_end,
            period_number=period_num,
            status="OPEN",
        )
        db.add(period)
        period_num += 1

        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    # Add OD period (opérations diverses)
    od_period = AccountingPeriod(
        tenant_id=tenant_id,
        fiscal_year_id=fy.id,
        dossier_id=data.dossier_id,
        name="OD",
        start_date=data.start_date,
        end_date=data.end_date,
        period_number=period_num,
        status="OPEN",
    )
    db.add(od_period)
    await db.flush()

    return fy


async def list_fiscal_years(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> list[FiscalYear]:
    await _ensure_dossier_exists(db, tenant_id, dossier_id)
    result = await db.execute(
        select(FiscalYear)
        .where(FiscalYear.tenant_id == tenant_id, FiscalYear.dossier_id == dossier_id)
        .order_by(FiscalYear.start_date.desc())
    )
    return list(result.scalars().all())


async def get_fiscal_year(
    db: AsyncSession, tenant_id: uuid.UUID, fy_id: uuid.UUID
) -> FiscalYear:
    result = await db.execute(
        select(FiscalYear)
        .where(FiscalYear.id == fy_id, FiscalYear.tenant_id == tenant_id)
        .options(selectinload(FiscalYear.periods))
    )
    fy = result.scalar_one_or_none()
    if not fy:
        raise NotFoundError("Fiscal year not found")
    await _ensure_dossier_exists(db, tenant_id, fy.dossier_id)
    return fy


async def lock_period(
    db: AsyncSession, tenant_id: uuid.UUID, period_id: uuid.UUID
) -> AccountingPeriod:
    result = await db.execute(
        select(AccountingPeriod).where(
            AccountingPeriod.id == period_id,
            AccountingPeriod.tenant_id == tenant_id,
        )
    )
    period = result.scalar_one_or_none()
    if not period:
        raise NotFoundError("Period not found")
    await _ensure_dossier_exists(db, tenant_id, period.dossier_id)
    if period.status != "OPEN":
        raise BadRequestError(f"Period is already {period.status}")

    period.status = "LOCKED"
    await db.flush()
    return period


async def create_audit_log(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id: str,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    await db.flush()
    return log
