import os
from datetime import date
from pathlib import Path
import subprocess

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://easy_app:easy_app@localhost:5432/easyaccounting_test",
)
os.environ.setdefault(
    "AUTH_DATABASE_URL",
    "postgresql+asyncpg://easy_auth:easy_auth@localhost:5432/easyaccounting_test",
)
os.environ.setdefault(
    "ALEMBIC_DATABASE_URL",
    "postgresql+asyncpg://easy_owner:easy_owner@localhost:5432/easyaccounting_test",
)

from app.database import (  # noqa: E402
    app_session_factory,
    auth_session_factory,
    dispose_engines,
)
from app.main import create_app  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parents[1]
OWNER_DB_URL = os.environ["ALEMBIC_DATABASE_URL"]


def _run_migrations() -> None:
    env = os.environ.copy()
    env["ALEMBIC_DATABASE_URL"] = OWNER_DB_URL
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=ROOT_DIR,
        env=env,
        check=True,
    )


@pytest_asyncio.fixture
async def owner_engine():
    engine = create_async_engine(OWNER_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def migrated_db(owner_engine):
    await dispose_engines()
    async with owner_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS app CASCADE"))
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO easy_owner"))
        await conn.execute(text("GRANT USAGE ON SCHEMA public TO easy_app, easy_auth"))

    _run_migrations()
    yield
    await dispose_engines()


@pytest_asyncio.fixture
async def app_db_session():
    async with app_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def auth_db_session():
    async with auth_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seed_data(client):
    register_payload = {
        "email": "admin@example.com",
        "password": "TestPass123",
        "first_name": "Admin",
        "last_name": "User",
        "company_name": "Tenant Alpha",
    }
    register_resp = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_resp.status_code == 200
    tokens = register_resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me = me_resp.json()

    companies_resp = await client.get("/api/v1/tenant/companies", headers=headers)
    assert companies_resp.status_code == 200
    companies = companies_resp.json()

    dossiers_resp = await client.get("/api/v1/tenant/dossiers", headers=headers)
    assert dossiers_resp.status_code == 200
    dossiers = dossiers_resp.json()

    client.headers["Authorization"] = headers["Authorization"]
    return {
        "token": tokens["access_token"],
        "headers": headers,
        "user": me,
        "tenant": {"id": me["tenant_id"], "name": "Tenant Alpha"},
        "company": companies[0],
        "dossier": dossiers[0],
    }


@pytest_asyncio.fixture
async def second_tenant(client):
    payload = {
        "email": "other-admin@example.com",
        "password": "TestPass123",
        "first_name": "Other",
        "last_name": "Admin",
        "company_name": "Tenant Beta",
    }
    register_resp = await client.post("/api/v1/auth/register", json=payload)
    assert register_resp.status_code == 200
    tokens = register_resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    dossiers_resp = await client.get("/api/v1/tenant/dossiers", headers=headers)
    assert me_resp.status_code == 200
    assert dossiers_resp.status_code == 200

    return {
        "token": tokens["access_token"],
        "headers": headers,
        "user": me_resp.json(),
        "tenant": {"id": me_resp.json()["tenant_id"], "name": "Tenant Beta"},
        "dossier": dossiers_resp.json()[0],
    }


@pytest.fixture
def future_fiscal_year_dates():
    year = date.today().year + 1
    return {
        "year": year,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "entry_date": f"{year}-01-15",
        "second_entry_date": f"{year}-01-20",
    }
