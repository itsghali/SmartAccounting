import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import TenantMixin, TimestampMixin, generate_uuid


class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        lazy="raise",
        foreign_keys="UserRole.user_id",
    )

    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_users_email_lowercase"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id_id"),
    )


class Role(Base, TenantMixin, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        lazy="raise",
        foreign_keys="RolePermission.role_id",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_role_tenant_name"),
        UniqueConstraint("tenant_id", "id", name="uq_roles_tenant_id_id"),
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)


class RolePermission(Base, TenantMixin):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    role: Mapped["Role"] = relationship(
        back_populates="permissions",
        foreign_keys=[role_id],
    )
    permission: Mapped["Permission"] = relationship()

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "role_id"],
            ["roles.tenant_id", "roles.id"],
            ondelete="CASCADE",
            name="fk_role_permissions_role_tenant",
        ),
        UniqueConstraint(
            "tenant_id",
            "role_id",
            "permission_id",
            name="uq_role_permissions_tenant_role_permission",
        ),
    )


class UserRole(Base, TenantMixin):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship(
        back_populates="user_roles",
        foreign_keys=[user_id],
    )
    role: Mapped["Role"] = relationship(foreign_keys=[role_id])

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            ondelete="CASCADE",
            name="fk_user_roles_user_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "role_id"],
            ["roles.tenant_id", "roles.id"],
            ondelete="CASCADE",
            name="fk_user_roles_role_tenant",
        ),
        UniqueConstraint(
            "tenant_id",
            "user_id",
            "role_id",
            name="uq_user_roles_tenant_user_role",
        ),
    )


class UserDossierAssignment(Base, TenantMixin, TimestampMixin):
    __tablename__ = "user_dossier_assignments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            ondelete="CASCADE",
            name="fk_user_dossier_assignments_user_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "dossier_id"],
            ["dossiers.tenant_id", "dossiers.id"],
            ondelete="CASCADE",
            name="fk_user_dossier_assignments_dossier_tenant",
        ),
        UniqueConstraint(
            "tenant_id",
            "user_id",
            "dossier_id",
            name="uq_user_dossier_assignments_tenant_user_dossier",
        ),
    )
