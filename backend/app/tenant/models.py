import uuid

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import TenantMixin, TimestampMixin, generate_uuid


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    status: Mapped[str] = mapped_column(String(50), default="active")

    companies: Mapped[list["Company"]] = relationship(back_populates="tenant", lazy="raise")


class Company(Base, TenantMixin, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_form: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ice: Mapped[str | None] = mapped_column(String(15), nullable=True)
    if_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rc: Mapped[str | None] = mapped_column(String(50), nullable=True)
    patente: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cnss_employer: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="companies")
    dossiers: Mapped[list["Dossier"]] = relationship(
        back_populates="company",
        lazy="raise",
        foreign_keys="Dossier.company_id",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_companies_tenant_id_id"),
    )


class Dossier(Base, TenantMixin, TimestampMixin):
    __tablename__ = "dossiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")

    company: Mapped["Company"] = relationship(
        back_populates="dossiers",
        foreign_keys=[company_id],
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "company_id"],
            ["companies.tenant_id", "companies.id"],
            name="fk_dossiers_company_tenant",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_dossiers_tenant_id_id"),
    )
