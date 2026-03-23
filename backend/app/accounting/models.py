import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import TenantMixin, TimestampMixin, generate_uuid


class Account(Base, TenantMixin, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    account_class: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-9
    account_type: Mapped[str] = mapped_column(
        String(20), default="detail"
    )  # detail, collective, centralizer
    nature: Mapped[str] = mapped_column(
        String(10), default="debit"
    )  # debit, credit
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_lettrable: Mapped[bool] = mapped_column(Boolean, default=False)
    default_tva_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    parent_number: Mapped[str | None] = mapped_column(String(10), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_accounts_dossier_tenant",
        ),
        UniqueConstraint("dossier_id", "number", name="uq_account_dossier_number"),
        UniqueConstraint("tenant_id", "id", name="uq_accounts_tenant_id_id"),
    )


class Journal(Base, TenantMixin, TimestampMixin):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    journal_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # achat, vente, tresorerie, od, an, situation
    counterpart_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_journals_dossier_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "counterpart_account_id"],
            ["accounts.tenant_id", "accounts.id"],
            name="fk_journals_counterpart_account_tenant",
        ),
        UniqueConstraint("dossier_id", "code", name="uq_journal_dossier_code"),
        UniqueConstraint("tenant_id", "id", name="uq_journals_tenant_id_id"),
    )


class ThirdParty(Base, TenantMixin, TimestampMixin):
    __tablename__ = "third_parties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    party_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # client, supplier, both
    ice: Mapped[str | None] = mapped_column(String(15), nullable=True)
    if_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rc: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    default_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_third_parties_dossier_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "default_account_id"],
            ["accounts.tenant_id", "accounts.id"],
            name="fk_third_parties_default_account_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_third_parties_tenant_id_id"),
    )


class JournalEntry(Base, TenantMixin, TimestampMixin):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    journal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journals.id"), nullable=False
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounting_periods.id"), nullable=False
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    piece_number: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="DRAFT"
    )  # DRAFT, VALIDATED
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reversal_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )

    lines: Mapped[list["JournalEntryLine"]] = relationship(
        back_populates="entry",
        lazy="raise",
        cascade="all, delete-orphan",
        foreign_keys="JournalEntryLine.entry_id",
    )
    journal: Mapped["Journal"] = relationship(lazy="raise", foreign_keys=[journal_id])
    period: Mapped["AccountingPeriod"] = relationship(
        lazy="raise",
        foreign_keys=[period_id],
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_journal_entries_dossier_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "journal_id"],
            ["journals.tenant_id", "journals.id"],
            name="fk_journal_entries_journal_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "period_id"],
            ["accounting_periods.tenant_id", "accounting_periods.id"],
            name="fk_journal_entries_period_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "reversal_of_id"],
            ["journal_entries.tenant_id", "journal_entries.id"],
            name="fk_journal_entries_reversal_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_journal_entries_tenant_id_id"),
    )

    @property
    def total_debit(self) -> Decimal:
        return sum((line.debit for line in self.lines), Decimal("0.00"))

    @property
    def total_credit(self) -> Decimal:
        return sum((line.credit for line in self.lines), Decimal("0.00"))

    @property
    def is_balanced(self) -> bool:
        return self.total_debit == self.total_credit


# Need to import for relationship reference
from app.core.models import AccountingPeriod  # noqa: E402


class JournalEntryLine(Base, TenantMixin):
    __tablename__ = "journal_entry_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    third_party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("third_parties.id"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    debit: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=Decimal("0.00")
    )
    credit: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=Decimal("0.00")
    )
    lettrage_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    entry: Mapped["JournalEntry"] = relationship(
        back_populates="lines",
        foreign_keys=[entry_id],
    )
    account: Mapped["Account"] = relationship(lazy="raise", foreign_keys=[account_id])

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "entry_id"],
            ["journal_entries.tenant_id", "journal_entries.id"],
            ondelete="CASCADE",
            name="fk_journal_entry_lines_entry_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "account_id"],
            ["accounts.tenant_id", "accounts.id"],
            name="fk_journal_entry_lines_account_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "third_party_id"],
            ["third_parties.tenant_id", "third_parties.id"],
            name="fk_journal_entry_lines_third_party_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_journal_entry_lines_tenant_id_id"),
    )
