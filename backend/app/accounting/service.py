import uuid
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.accounting.models import (
    Account,
    Journal,
    JournalEntry,
    JournalEntryLine,
    ThirdParty,
)
from app.accounting.schemas import (
    AccountCreate,
    EntryLineCreate,
    JournalCreate,
    JournalEntryCreate,
    ThirdPartyCreate,
)
from app.core.models import AccountingPeriod, FiscalYear
from app.core.service import create_audit_log
from app.shared.exceptions import (
    BadRequestError,
    ImmutableEntryError,
    NotFoundError,
    PeriodClosedError,
    UnbalancedEntryError,
)
from app.tenant.models import Dossier


# ──────────────────── Dashboard Stats ────────────────────


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


async def get_dashboard_stats(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> dict:
    """Aggregate counts and totals for the dashboard."""
    await _ensure_dossier_exists(db, tenant_id, dossier_id)

    accounts_count = (
        await db.execute(
            select(func.count(Account.id)).where(
                Account.tenant_id == tenant_id,
                Account.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    journals_count = (
        await db.execute(
            select(func.count(Journal.id)).where(
                Journal.tenant_id == tenant_id,
                Journal.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    entries_count = (
        await db.execute(
            select(func.count(JournalEntry.id)).where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    draft_entries_count = (
        await db.execute(
            select(func.count(JournalEntry.id)).where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.dossier_id == dossier_id,
                JournalEntry.status == "DRAFT",
            )
        )
    ).scalar() or 0

    validated_entries_count = (
        await db.execute(
            select(func.count(JournalEntry.id)).where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.dossier_id == dossier_id,
                JournalEntry.status == "VALIDATED",
            )
        )
    ).scalar() or 0

    fiscal_years_count = (
        await db.execute(
            select(func.count(FiscalYear.id)).where(
                FiscalYear.tenant_id == tenant_id,
                FiscalYear.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    open_fiscal_years_count = (
        await db.execute(
            select(func.count(FiscalYear.id)).where(
                FiscalYear.tenant_id == tenant_id,
                FiscalYear.dossier_id == dossier_id,
                FiscalYear.status == "OPEN",
            )
        )
    ).scalar() or 0

    periods_count = (
        await db.execute(
            select(func.count(AccountingPeriod.id)).where(
                AccountingPeriod.tenant_id == tenant_id,
                AccountingPeriod.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    open_periods_count = (
        await db.execute(
            select(func.count(AccountingPeriod.id)).where(
                AccountingPeriod.tenant_id == tenant_id,
                AccountingPeriod.dossier_id == dossier_id,
                AccountingPeriod.status == "OPEN",
            )
        )
    ).scalar() or 0

    locked_periods_count = (
        await db.execute(
            select(func.count(AccountingPeriod.id)).where(
                AccountingPeriod.tenant_id == tenant_id,
                AccountingPeriod.dossier_id == dossier_id,
                AccountingPeriod.status == "LOCKED",
            )
        )
    ).scalar() or 0

    third_parties_count = (
        await db.execute(
            select(func.count(ThirdParty.id)).where(
                ThirdParty.tenant_id == tenant_id,
                ThirdParty.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    # Total debit/credit across all entries
    totals = (
        await db.execute(
            select(
                func.coalesce(func.sum(JournalEntryLine.debit), 0),
                func.coalesce(func.sum(JournalEntryLine.credit), 0),
            )
            .join(JournalEntry, JournalEntryLine.entry_id == JournalEntry.id)
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.dossier_id == dossier_id,
                JournalEntry.status == "VALIDATED",
            )
        )
    ).one()

    return {
        "accounts_count": accounts_count,
        "journals_count": journals_count,
        "entries_count": entries_count,
        "draft_entries_count": draft_entries_count,
        "validated_entries_count": validated_entries_count,
        "fiscal_years_count": fiscal_years_count,
        "open_fiscal_years_count": open_fiscal_years_count,
        "periods_count": periods_count,
        "open_periods_count": open_periods_count,
        "locked_periods_count": locked_periods_count,
        "third_parties_count": third_parties_count,
        "total_debit": str(totals[0]),
        "total_credit": str(totals[1]),
    }


# ──────────────────── Accounts ────────────────────


async def list_accounts(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> list[Account]:
    await _ensure_dossier_exists(db, tenant_id, dossier_id)
    result = await db.execute(
        select(Account)
        .where(Account.tenant_id == tenant_id, Account.dossier_id == dossier_id)
        .order_by(Account.number)
    )
    return list(result.scalars().all())


async def create_account(
    db: AsyncSession, tenant_id: uuid.UUID, data: AccountCreate
) -> Account:
    await _ensure_dossier_exists(db, tenant_id, data.dossier_id)

    tva = None
    if data.default_tva_rate is not None:
        try:
            tva = Decimal(data.default_tva_rate)
        except InvalidOperation:
            raise BadRequestError("Invalid TVA rate format")

    account = Account(
        tenant_id=tenant_id,
        dossier_id=data.dossier_id,
        number=data.number,
        label=data.label,
        account_class=data.account_class,
        account_type=data.account_type,
        nature=data.nature,
        is_lettrable=data.is_lettrable,
        default_tva_rate=tva,
        parent_number=data.parent_number,
    )
    db.add(account)
    await db.flush()
    return account


async def get_account(
    db: AsyncSession, tenant_id: uuid.UUID, account_id: uuid.UUID
) -> Account:
    result = await db.execute(
        select(Account).where(
            Account.id == account_id, Account.tenant_id == tenant_id
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise NotFoundError("Account not found")
    await _ensure_dossier_exists(db, tenant_id, account.dossier_id)
    return account


# ──────────────────── Journals ────────────────────


async def list_journals(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> list[Journal]:
    await _ensure_dossier_exists(db, tenant_id, dossier_id)
    result = await db.execute(
        select(Journal)
        .where(Journal.tenant_id == tenant_id, Journal.dossier_id == dossier_id)
        .order_by(Journal.code)
    )
    return list(result.scalars().all())


async def create_journal(
    db: AsyncSession, tenant_id: uuid.UUID, data: JournalCreate
) -> Journal:
    await _ensure_dossier_exists(db, tenant_id, data.dossier_id)
    journal = Journal(tenant_id=tenant_id, **data.model_dump())
    db.add(journal)
    await db.flush()
    return journal


# ──────────────────── Third Parties ────────────────────


async def list_third_parties(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> list[ThirdParty]:
    await _ensure_dossier_exists(db, tenant_id, dossier_id)
    result = await db.execute(
        select(ThirdParty)
        .where(ThirdParty.tenant_id == tenant_id, ThirdParty.dossier_id == dossier_id)
        .order_by(ThirdParty.name)
    )
    return list(result.scalars().all())


async def create_third_party(
    db: AsyncSession, tenant_id: uuid.UUID, data: ThirdPartyCreate
) -> ThirdParty:
    await _ensure_dossier_exists(db, tenant_id, data.dossier_id)
    tp = ThirdParty(tenant_id=tenant_id, **data.model_dump())
    db.add(tp)
    await db.flush()
    return tp


# ──────────────────── Journal Entries ────────────────────


async def _generate_piece_number(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    journal_id: uuid.UUID,
    period_id: uuid.UUID,
) -> str:
    result = await db.execute(
        select(func.count(JournalEntry.id)).where(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.journal_id == journal_id,
            JournalEntry.period_id == period_id,
        )
    )
    count = result.scalar() or 0

    # Get journal code for the prefix
    journal_result = await db.execute(
        select(Journal.code).where(Journal.id == journal_id)
    )
    journal_code = journal_result.scalar() or "XX"

    # Get period name
    period_result = await db.execute(
        select(AccountingPeriod.name).where(AccountingPeriod.id == period_id)
    )
    period_name = period_result.scalar() or "00"
    period_short = period_name.replace("/", "")

    return f"{journal_code}-{period_short}-{count + 1:04d}"


async def _validate_period_is_open(
    db: AsyncSession, tenant_id: uuid.UUID, period_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(AccountingPeriod).where(
            AccountingPeriod.id == period_id,
            AccountingPeriod.tenant_id == tenant_id,
        )
    )
    period = result.scalar_one_or_none()
    if not period:
        raise NotFoundError("Accounting period not found")
    if period.status != "OPEN":
        raise PeriodClosedError()


def _parse_line_amount(value: str, field_name: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise BadRequestError(f"Invalid {field_name} amount format")
    if amount < 0:
        raise BadRequestError(f"{field_name} amount cannot be negative")
    return amount


async def create_journal_entry(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: JournalEntryCreate
) -> JournalEntry:
    await _ensure_dossier_exists(db, tenant_id, data.dossier_id)
    await _validate_period_is_open(db, tenant_id, data.period_id)

    # Parse and validate lines
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    parsed_lines: list[tuple[EntryLineCreate, Decimal, Decimal]] = []

    for line in data.lines:
        debit = _parse_line_amount(line.debit, "debit")
        credit = _parse_line_amount(line.credit, "credit")

        if debit > 0 and credit > 0:
            raise BadRequestError(
                "A line cannot have both debit and credit amounts"
            )
        if debit == 0 and credit == 0:
            raise BadRequestError(
                "A line must have either a debit or credit amount"
            )

        total_debit += debit
        total_credit += credit
        parsed_lines.append((line, debit, credit))

    if total_debit != total_credit:
        raise UnbalancedEntryError()

    piece_number = await _generate_piece_number(
        db, tenant_id, data.journal_id, data.period_id
    )

    entry = JournalEntry(
        tenant_id=tenant_id,
        dossier_id=data.dossier_id,
        journal_id=data.journal_id,
        period_id=data.period_id,
        entry_date=data.entry_date,
        piece_number=piece_number,
        label=data.label,
        reference=data.reference,
        status="DRAFT",
    )
    db.add(entry)
    await db.flush()

    for idx, (line, debit, credit) in enumerate(parsed_lines, start=1):
        entry_line = JournalEntryLine(
            tenant_id=tenant_id,
            entry_id=entry.id,
            line_number=idx,
            account_id=line.account_id,
            third_party_id=line.third_party_id,
            label=line.label,
            debit=debit,
            credit=credit,
        )
        db.add(entry_line)

    await db.flush()

    await create_audit_log(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        action="CREATE",
        entity_type="JournalEntry",
        entity_id=str(entry.id),
        new_values={"piece_number": piece_number, "label": data.label},
    )

    # Re-fetch with relationships loaded
    return await get_journal_entry(db, tenant_id, entry.id)


async def list_journal_entries(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dossier_id: uuid.UUID,
    journal_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[JournalEntry]:
    await _ensure_dossier_exists(db, tenant_id, dossier_id)

    query = (
        select(JournalEntry)
        .where(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.dossier_id == dossier_id,
        )
        .options(
            selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account),
            selectinload(JournalEntry.journal),
            selectinload(JournalEntry.period),
        )
    )
    if journal_id:
        query = query.where(JournalEntry.journal_id == journal_id)
    if period_id:
        query = query.where(JournalEntry.period_id == period_id)
    if status:
        query = query.where(JournalEntry.status == status)
    query = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.piece_number)

    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_journal_entry(
    db: AsyncSession, tenant_id: uuid.UUID, entry_id: uuid.UUID
) -> JournalEntry:
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.id == entry_id, JournalEntry.tenant_id == tenant_id)
        .options(
            selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account),
            selectinload(JournalEntry.journal),
            selectinload(JournalEntry.period),
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundError("Journal entry not found")
    await _ensure_dossier_exists(db, tenant_id, entry.dossier_id)
    return entry


async def validate_entry(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, entry_id: uuid.UUID
) -> JournalEntry:
    entry = await get_journal_entry(db, tenant_id, entry_id)

    if entry.status != "DRAFT":
        raise ImmutableEntryError()

    await _validate_period_is_open(db, tenant_id, entry.period_id)

    if not entry.is_balanced:
        raise UnbalancedEntryError()

    entry.status = "VALIDATED"
    await db.flush()

    await create_audit_log(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        action="VALIDATE",
        entity_type="JournalEntry",
        entity_id=str(entry.id),
        old_values={"status": "DRAFT"},
        new_values={"status": "VALIDATED"},
    )

    return entry


async def reverse_entry(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, entry_id: uuid.UUID
) -> JournalEntry:
    original = await get_journal_entry(db, tenant_id, entry_id)

    if original.status != "VALIDATED":
        raise BadRequestError("Only validated entries can be reversed")

    await _validate_period_is_open(db, tenant_id, original.period_id)

    piece_number = await _generate_piece_number(
        db, tenant_id, original.journal_id, original.period_id
    )

    reversal = JournalEntry(
        tenant_id=tenant_id,
        dossier_id=original.dossier_id,
        journal_id=original.journal_id,
        period_id=original.period_id,
        entry_date=original.entry_date,
        piece_number=piece_number,
        label=f"Contrepassation de {original.piece_number}",
        reference=original.piece_number,
        reversal_of_id=original.id,
        status="DRAFT",
    )
    db.add(reversal)
    await db.flush()

    for line in original.lines:
        reversal_line = JournalEntryLine(
            tenant_id=tenant_id,
            entry_id=reversal.id,
            line_number=line.line_number,
            account_id=line.account_id,
            third_party_id=line.third_party_id,
            label=line.label,
            debit=line.credit,   # Swap debit/credit
            credit=line.debit,
        )
        db.add(reversal_line)

    await db.flush()

    await create_audit_log(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        action="REVERSE",
        entity_type="JournalEntry",
        entity_id=str(original.id),
        new_values={"reversal_id": str(reversal.id)},
    )

    return await get_journal_entry(db, tenant_id, reversal.id)
