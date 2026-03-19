import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.seed import seed_dossier_defaults
from app.shared.exceptions import BadRequestError, NotFoundError
from app.tenant.models import Company, Dossier
from app.tenant.schemas import CompanyCreate, CompanyUpdate, DossierCreate


async def list_companies(db: AsyncSession, tenant_id: uuid.UUID) -> list[Company]:
    result = await db.execute(
        select(Company).where(Company.tenant_id == tenant_id).order_by(Company.name)
    )
    return list(result.scalars().all())


async def create_company(
    db: AsyncSession, tenant_id: uuid.UUID, data: CompanyCreate
) -> Company:
    company = Company(tenant_id=tenant_id, **data.model_dump())
    db.add(company)
    await db.flush()
    return company


async def get_company(
    db: AsyncSession, tenant_id: uuid.UUID, company_id: uuid.UUID
) -> Company:
    result = await db.execute(
        select(Company).where(
            Company.id == company_id, Company.tenant_id == tenant_id
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundError("Company not found")
    return company


async def update_company(
    db: AsyncSession, tenant_id: uuid.UUID, company_id: uuid.UUID, data: CompanyUpdate
) -> Company:
    result = await db.execute(
        select(Company).where(
            Company.id == company_id, Company.tenant_id == tenant_id
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundError("Company not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.flush()
    return company


async def list_dossiers(db: AsyncSession, tenant_id: uuid.UUID) -> list[Dossier]:
    result = await db.execute(
        select(Dossier)
        .where(
            Dossier.tenant_id == tenant_id,
            Dossier.status != "deleted",
        )
        .order_by(Dossier.name)
    )
    return list(result.scalars().all())


async def create_dossier(
    db: AsyncSession, tenant_id: uuid.UUID, data: DossierCreate
) -> Dossier:
    dossier = Dossier(tenant_id=tenant_id, **data.model_dump())
    db.add(dossier)
    await db.flush()

    # Auto-seed PCM accounts and default journals for the new dossier
    await seed_dossier_defaults(db, tenant_id, dossier.id)

    return dossier


async def get_dossier(
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
        raise NotFoundError("Dossier not found")
    return dossier


async def delete_dossier(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> None:
    dossier = await get_dossier(db, tenant_id, dossier_id)
    if dossier.status == "deleted":
        raise BadRequestError("Le dossier est deja supprime")

    dossier.status = "deleted"
    await db.flush()
