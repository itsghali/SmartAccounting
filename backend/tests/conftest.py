import os
import uuid
from decimal import Decimal

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.models import Role, User, UserRole
from app.auth.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import create_app
from app.tenant.models import Company, Dossier, Tenant

default_database_url = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://easy:easy@localhost:5432/easyaccounting",
)
default_test_database = os.environ.get("TEST_DB_NAME", "easyaccounting_test")
default_test_db_url = str(
    make_url(default_database_url).set(database=default_test_database)
)
TEST_DB_URL = os.environ.get("TEST_DB_URL", default_test_db_url)


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession):
    tenant = Tenant(name="Test Tenant", plan="free", status="active")
    db_session.add(tenant)
    await db_session.flush()

    company = Company(tenant_id=tenant.id, name="Test Company", legal_form="SARL")
    db_session.add(company)
    await db_session.flush()

    dossier = Dossier(tenant_id=tenant.id, company_id=company.id, name="Dossier Test", status="active")
    db_session.add(dossier)
    await db_session.flush()

    role = Role(tenant_id=tenant.id, name="Administrateur", is_system=True)
    db_session.add(role)
    await db_session.flush()

    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        password_hash=hash_password("TestPass123"),
        first_name="Test",
        last_name="User",
    )
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.flush()

    token = create_access_token(user.id, tenant.id, "Administrateur")
    await db_session.commit()

    return {
        "tenant": tenant,
        "company": company,
        "dossier": dossier,
        "user": user,
        "role": role,
        "token": token,
    }


@pytest_asyncio.fixture
async def client(db_session, seed_data):
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers["Authorization"] = f"Bearer {seed_data['token']}"
        yield ac
