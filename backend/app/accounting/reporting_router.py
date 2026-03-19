"""
Reporting endpoints: Balance Generale, Grand Livre, Bilan, CPC.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.reporting import (
    get_balance_generale,
    get_bilan,
    get_cpc,
    get_grand_livre,
)
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/reporting", tags=["reporting"])


@router.get("/balance-generale")
async def balance_generale(
    dossier_id: uuid.UUID = Query(...),
    fiscal_year_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    validated_only: bool = True,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_balance_generale(
        db,
        current_user["tenant_id"],
        dossier_id,
        fiscal_year_id=fiscal_year_id,
        period_id=period_id,
        validated_only=validated_only,
    )


@router.get("/grand-livre")
async def grand_livre(
    dossier_id: uuid.UUID = Query(...),
    account_number: str | None = None,
    fiscal_year_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    validated_only: bool = True,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_grand_livre(
        db,
        current_user["tenant_id"],
        dossier_id,
        account_number=account_number,
        fiscal_year_id=fiscal_year_id,
        period_id=period_id,
        validated_only=validated_only,
    )


@router.get("/bilan")
async def bilan(
    dossier_id: uuid.UUID = Query(...),
    fiscal_year_id: uuid.UUID | None = None,
    validated_only: bool = True,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_bilan(
        db,
        current_user["tenant_id"],
        dossier_id,
        fiscal_year_id=fiscal_year_id,
        validated_only=validated_only,
    )


@router.get("/cpc")
async def cpc(
    dossier_id: uuid.UUID = Query(...),
    fiscal_year_id: uuid.UUID | None = None,
    validated_only: bool = True,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_cpc(
        db,
        current_user["tenant_id"],
        dossier_id,
        fiscal_year_id=fiscal_year_id,
        validated_only=validated_only,
    )
