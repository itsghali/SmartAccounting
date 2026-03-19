import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import Role, User, UserRole
from app.auth.schemas import PasswordChange, ProfileUpdate, RegisterRequest, UserCreateRequest
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.accounting.seed import seed_dossier_defaults
from app.shared.exceptions import BadRequestError, NotFoundError
from app.tenant.models import Company, Dossier, Tenant

SYSTEM_ROLE_DEFINITIONS: list[tuple[str, str]] = [
    ("Administrateur", "Administration complete du tenant"),
    ("Responsable", "Gestion des utilisateurs et des dossiers"),
    ("Collaborateur", "Acces operationnel standard"),
]


async def ensure_system_roles(
    db: AsyncSession, tenant_id: uuid.UUID
) -> dict[str, Role]:
    result = await db.execute(
        select(Role).where(Role.tenant_id == tenant_id)
    )
    existing_roles = {role.name: role for role in result.scalars().all()}

    for role_name, description in SYSTEM_ROLE_DEFINITIONS:
        if role_name not in existing_roles:
            role = Role(
                tenant_id=tenant_id,
                name=role_name,
                description=description,
                is_system=True,
            )
            db.add(role)
            await db.flush()
            existing_roles[role_name] = role

    return existing_roles


async def register_user(db: AsyncSession, data: RegisterRequest) -> dict:
    existing = await db.execute(
        select(User).where(User.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise BadRequestError("Email already registered")

    tenant = Tenant(name=data.company_name, plan="free", status="active")
    db.add(tenant)
    await db.flush()

    company = Company(
        tenant_id=tenant.id,
        name=data.company_name,
        legal_form="SARL",
    )
    db.add(company)
    await db.flush()

    dossier = Dossier(
        tenant_id=tenant.id,
        company_id=company.id,
        name=f"Dossier {data.company_name}",
        status="active",
    )
    db.add(dossier)
    await db.flush()

    # Auto-seed PCM accounts and default journals for the first dossier
    await seed_dossier_defaults(db, tenant.id, dossier.id)

    roles = await ensure_system_roles(db, tenant.id)
    admin_role = roles["Administrateur"]

    user = User(
        tenant_id=tenant.id,
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.flush()

    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db.add(user_role)
    await db.flush()

    access_token = create_access_token(user.id, tenant.id, "Administrateur")
    refresh_token = create_refresh_token(user.id, tenant.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> dict:
    result = await db.execute(
        select(User)
        .where(User.email == email)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise BadRequestError("Invalid email or password")

    if not user.is_active:
        raise BadRequestError("Account is disabled")

    user = await ensure_user_has_system_role(db, user)

    role_name = "Collaborateur"
    if user.user_roles:
        role_name = user.user_roles[0].role.name

    access_token = create_access_token(user.id, user.tenant_id, role_name)
    refresh_token = create_refresh_token(user.id, user.tenant_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def ensure_user_has_system_role(db: AsyncSession, user: User) -> User:
    if user.user_roles:
        return user

    roles = await ensure_system_roles(db, user.tenant_id)
    existing_assignments = await db.execute(
        select(UserRole)
        .join(User, User.id == UserRole.user_id)
        .where(User.tenant_id == user.tenant_id)
        .limit(1)
    )
    default_role = (
        roles["Administrateur"]
        if existing_assignments.scalar_one_or_none() is None
        else roles["Collaborateur"]
    )

    db.add(UserRole(user_id=user.id, role_id=default_role.id))
    await db.flush()
    return await get_user_by_id(db, user.id)


async def list_users(db: AsyncSession, tenant_id: uuid.UUID) -> list[User]:
    result = await db.execute(
        select(User)
        .where(User.tenant_id == tenant_id)
        .order_by(User.first_name, User.last_name, User.email)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
    )
    return list(result.scalars().unique().all())


async def list_roles(db: AsyncSession, tenant_id: uuid.UUID) -> list[Role]:
    roles = await ensure_system_roles(db, tenant_id)
    return sorted(roles.values(), key=lambda role: role.name)


async def create_user(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    data: UserCreateRequest,
    actor_role_names: set[str] | None = None,
) -> User:
    existing = await db.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == data.email,
        )
    )
    if existing.scalar_one_or_none():
        raise BadRequestError("Un utilisateur avec cet email existe deja")

    roles = await ensure_system_roles(db, tenant_id)
    role = roles.get(data.role_name)
    if not role:
        raise BadRequestError("Role invalide")
    if actor_role_names is not None and "Administrateur" not in actor_role_names:
        if data.role_name in {"Administrateur", "Responsable"}:
            raise BadRequestError(
                "Seul un Administrateur peut creer un Administrateur ou un Responsable"
            )

    user = User(
        tenant_id=tenant_id,
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    db.add(UserRole(user_id=user.id, role_id=role.id))
    await db.flush()

    return await get_user_by_id(db, user.id)


async def update_profile(
    db: AsyncSession, user: User, data: ProfileUpdate
) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    # Reload with roles
    return await get_user_by_id(db, user.id)


async def change_password(
    db: AsyncSession, user: User, data: PasswordChange
) -> None:
    if not verify_password(data.current_password, user.password_hash):
        raise BadRequestError("Mot de passe actuel incorrect")
    user.password_hash = hash_password(data.new_password)
    await db.flush()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")
    return user
