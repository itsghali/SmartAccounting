import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import TenantMixin, TimestampMixin, generate_uuid


class FiscalYear(Base, TenantMixin, TimestampMixin):
    __tablename__ = "fiscal_years"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="CREATED"
    )  # CREATED, OPEN, PRE_CLOSING, CLOSED, REOPENED

    periods: Mapped[list["AccountingPeriod"]] = relationship(
        back_populates="fiscal_year",
        lazy="raise",
        order_by="AccountingPeriod.period_number",
        foreign_keys="AccountingPeriod.fiscal_year_id",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_fiscal_years_dossier_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_fiscal_years_tenant_id_id"),
    )


class AccountingPeriod(Base, TenantMixin, TimestampMixin):
    __tablename__ = "accounting_periods"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    fiscal_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_years.id"), nullable=False
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="OPEN"
    )  # OPEN, LOCKED, CLOSED

    fiscal_year: Mapped["FiscalYear"] = relationship(
        back_populates="periods",
        foreign_keys=[fiscal_year_id],
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "fiscal_year_id"],
            ["fiscal_years.tenant_id", "fiscal_years.id"],
            name="fk_accounting_periods_fiscal_year_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            name="fk_accounting_periods_dossier_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_accounting_periods_tenant_id_id"),
    )


class AuditLog(Base, TenantMixin):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_audit_logs_tenant_id_id"),
    )


class Document(Base, TenantMixin, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_documents_tenant_id_id"),
    )


class DocumentLink(Base, TenantMixin, TimestampMixin):
    __tablename__ = "document_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.id"],
            ondelete="CASCADE",
            name="fk_document_links_document_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_document_links_tenant_id_id"),
    )
