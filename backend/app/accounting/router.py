import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.schemas import (
    AccountCreate,
    AccountResponse,
    DashboardStatsResponse,
    JournalCreate,
    JournalEntryCreate,
    JournalEntryResponse,
    JournalResponse,
    EntryLineResponse,
    ThirdPartyCreate,
    ThirdPartyResponse,
)
from app.accounting.seed import seed_dossier_defaults
from app.accounting.service import (
    create_account,
    create_journal,
    create_journal_entry,
    create_third_party,
    get_account,
    get_dashboard_stats,
    get_journal_entry,
    list_accounts,
    list_journal_entries,
    list_journals,
    list_third_parties,
    reverse_entry,
    validate_entry,
)
from app.database import get_app_db
from app.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/accounting", tags=["accounting"])


# ──────────────────── Dashboard Stats ────────────────────


@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
async def get_stats(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    return await get_dashboard_stats(db, current_user["tenant_id"], dossier_id)


@router.post("/seed-defaults")
async def post_seed_defaults(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(require_permission("admin.seed")),
    db: AsyncSession = Depends(get_app_db),
):
    """Manually seed PCM accounts and default journals for an existing dossier."""
    result = await seed_dossier_defaults(
        db, current_user["tenant_id"], dossier_id
    )
    return result


# ──────────────────── Accounts ────────────────────


@router.get("/accounts", response_model=list[AccountResponse])
async def get_accounts(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    return await list_accounts(db, current_user["tenant_id"], dossier_id)


@router.post("/accounts", response_model=AccountResponse, status_code=201)
async def post_account(
    data: AccountCreate,
    current_user=Depends(require_permission("comptabilite.write")),
    db: AsyncSession = Depends(get_app_db),
):
    return await create_account(db, current_user["tenant_id"], data)


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account_detail(
    account_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    return await get_account(db, current_user["tenant_id"], account_id)


# ──────────────────── Journals ────────────────────


@router.get("/journals", response_model=list[JournalResponse])
async def get_journals(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    return await list_journals(db, current_user["tenant_id"], dossier_id)


@router.post("/journals", response_model=JournalResponse, status_code=201)
async def post_journal(
    data: JournalCreate,
    current_user=Depends(require_permission("comptabilite.write")),
    db: AsyncSession = Depends(get_app_db),
):
    return await create_journal(db, current_user["tenant_id"], data)


# ──────────────────── Third Parties ────────────────────


@router.get("/third-parties", response_model=list[ThirdPartyResponse])
async def get_third_parties(
    dossier_id: uuid.UUID = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    return await list_third_parties(db, current_user["tenant_id"], dossier_id)


@router.post("/third-parties", response_model=ThirdPartyResponse, status_code=201)
async def post_third_party(
    data: ThirdPartyCreate,
    current_user=Depends(require_permission("comptabilite.write")),
    db: AsyncSession = Depends(get_app_db),
):
    return await create_third_party(db, current_user["tenant_id"], data)


# ──────────────────── Journal Entries ────────────────────


def _entry_to_response(entry) -> JournalEntryResponse:
    lines = []
    for line in entry.lines:
        lines.append(
            EntryLineResponse(
                id=line.id,
                line_number=line.line_number,
                account_id=line.account_id,
                label=line.label,
                debit=str(line.debit),
                credit=str(line.credit),
                third_party_id=line.third_party_id,
                lettrage_code=line.lettrage_code,
                account_number=line.account.number if line.account else None,
                account_label=line.account.label if line.account else None,
            )
        )
    return JournalEntryResponse(
        id=entry.id,
        dossier_id=entry.dossier_id,
        journal_id=entry.journal_id,
        period_id=entry.period_id,
        entry_date=entry.entry_date,
        piece_number=entry.piece_number,
        label=entry.label,
        status=entry.status,
        reference=entry.reference,
        reversal_of_id=entry.reversal_of_id,
        lines=lines,
        total_debit=str(entry.total_debit),
        total_credit=str(entry.total_credit),
    )


@router.get("/entries", response_model=list[JournalEntryResponse])
async def get_entries(
    dossier_id: uuid.UUID = Query(...),
    journal_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    status: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    entries = await list_journal_entries(
        db, current_user["tenant_id"], dossier_id, journal_id, period_id, status
    )
    return [_entry_to_response(e) for e in entries]


@router.post("/entries", response_model=JournalEntryResponse, status_code=201)
async def post_entry(
    data: JournalEntryCreate,
    current_user=Depends(require_permission("comptabilite.write")),
    db: AsyncSession = Depends(get_app_db),
):
    entry = await create_journal_entry(
        db, current_user["tenant_id"], current_user["user"].id, data
    )
    return _entry_to_response(entry)


@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_entry_detail(
    entry_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    entry = await get_journal_entry(db, current_user["tenant_id"], entry_id)
    return _entry_to_response(entry)


@router.post("/entries/{entry_id}/validate", response_model=JournalEntryResponse)
async def post_validate_entry(
    entry_id: uuid.UUID,
    current_user=Depends(require_permission("comptabilite.validate")),
    db: AsyncSession = Depends(get_app_db),
):
    entry = await validate_entry(
        db, current_user["tenant_id"], current_user["user"].id, entry_id
    )
    return _entry_to_response(entry)


@router.post("/entries/{entry_id}/reverse", response_model=JournalEntryResponse)
async def post_reverse_entry(
    entry_id: uuid.UUID,
    current_user=Depends(require_permission("comptabilite.validate")),
    db: AsyncSession = Depends(get_app_db),
):
    entry = await reverse_entry(
        db, current_user["tenant_id"], current_user["user"].id, entry_id
    )
    return _entry_to_response(entry)
