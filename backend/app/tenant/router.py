import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.tenant.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    DossierCreate,
    DossierResponse,
)
from app.tenant.service import (
    create_company,
    delete_dossier,
    create_dossier,
    get_company,
    get_dossier,
    list_companies,
    list_dossiers,
    update_company,
)

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.get("/companies", response_model=list[CompanyResponse])
async def get_companies(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_companies(db, current_user["tenant_id"])


@router.post("/companies", response_model=CompanyResponse, status_code=201)
async def post_company(
    data: CompanyCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_company(db, current_user["tenant_id"], data)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company_detail(
    company_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_company(db, current_user["tenant_id"], uuid.UUID(company_id))


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def put_company(
    company_id: str,
    data: CompanyUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_company(db, current_user["tenant_id"], uuid.UUID(company_id), data)


@router.get("/dossiers", response_model=list[DossierResponse])
async def get_dossiers(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_dossiers(db, current_user["tenant_id"])


@router.post("/dossiers", response_model=DossierResponse, status_code=201)
async def post_dossier(
    data: DossierCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_dossier(db, current_user["tenant_id"], data)


@router.get("/dossiers/{dossier_id}", response_model=DossierResponse)
async def get_dossier_detail(
    dossier_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_dossier(db, current_user["tenant_id"], uuid.UUID(dossier_id))


@router.delete(
    "/dossiers/{dossier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_dossier_route(
    dossier_id: str,
    current_user=Depends(require_roles("Administrateur", "Responsable")),
    db: AsyncSession = Depends(get_db),
):
    await delete_dossier(db, current_user["tenant_id"], uuid.UUID(dossier_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
