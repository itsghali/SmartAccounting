import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.database import apply_rls_context


RLS_TABLES = {
    "companies",
    "dossiers",
    "users",
    "roles",
    "role_permissions",
    "user_roles",
    "user_dossier_assignments",
    "fiscal_years",
    "accounting_periods",
    "audit_logs",
    "documents",
    "document_links",
    "accounts",
    "journals",
    "third_parties",
    "journal_entries",
    "journal_entry_lines",
}


async def test_database_roles_are_separated(app_db_session, auth_db_session):
    await apply_rls_context(app_db_session, None, None)
    app_role = (await app_db_session.execute(text("select current_user"))).scalar_one()
    auth_role = (await auth_db_session.execute(text("select current_user"))).scalar_one()

    assert app_role == "easy_app"
    assert auth_role == "easy_auth"


async def test_register_and_login_normalize_email(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "UPPERCASE.ADMIN@EXAMPLE.COM ",
            "password": "TestPass123",
            "first_name": "Upper",
            "last_name": "Case",
            "company_name": "Tenant Gamma",
        },
    )
    assert register_resp.status_code == 200

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "uppercase.admin@example.com", "password": "TestPass123"},
    )
    assert login_resp.status_code == 200


async def test_tenant_isolation_in_api_reads(client, seed_data, second_tenant):
    resp = await client.get("/api/v1/tenant/dossiers", headers=seed_data["headers"])
    assert resp.status_code == 200
    dossier_ids = {dossier["id"] for dossier in resp.json()}

    assert seed_data["dossier"]["id"] in dossier_ids
    assert second_tenant["dossier"]["id"] not in dossier_ids


async def test_tenant_isolation_in_sql_reads(app_db_session, seed_data, second_tenant):
    await apply_rls_context(
        app_db_session,
        seed_data["tenant"]["id"],
        seed_data["user"]["id"],
    )
    result = await app_db_session.execute(text("select id from dossiers"))
    dossier_ids = {str(row[0]) for row in result}

    assert seed_data["dossier"]["id"] in dossier_ids
    assert second_tenant["dossier"]["id"] not in dossier_ids


async def test_cross_tenant_insert_is_blocked(app_db_session, seed_data, second_tenant):
    await apply_rls_context(
        app_db_session,
        seed_data["tenant"]["id"],
        seed_data["user"]["id"],
    )

    with pytest.raises((IntegrityError, DBAPIError)):
        await app_db_session.execute(
            text(
                """
                insert into accounts (
                    id, dossier_id, number, label, account_class, account_type,
                    nature, is_system, is_lettrable, tenant_id
                ) values (
                    :id, :dossier_id, :number, :label, :account_class, :account_type,
                    :nature, :is_system, :is_lettrable, :tenant_id
                )
                """
            ),
            {
                "id": uuid.uuid4(),
                "dossier_id": second_tenant["dossier"]["id"],
                "number": "9999",
                "label": "Cross tenant forbidden",
                "account_class": 9,
                "account_type": "detail",
                "nature": "debit",
                "is_system": False,
                "is_lettrable": False,
                "tenant_id": seed_data["tenant"]["id"],
            },
        )


async def test_cross_tenant_update_is_blocked(app_db_session, seed_data, second_tenant):
    await apply_rls_context(
        app_db_session,
        seed_data["tenant"]["id"],
        seed_data["user"]["id"],
    )

    result = await app_db_session.execute(
        text(
            """
            update dossiers
            set name = 'HACKED'
            where id = :dossier_id
            returning id
            """
        ),
        {"dossier_id": second_tenant["dossier"]["id"]},
    )
    assert result.first() is None


async def test_cross_tenant_delete_is_blocked(app_db_session, seed_data, second_tenant):
    await apply_rls_context(
        app_db_session,
        seed_data["tenant"]["id"],
        seed_data["user"]["id"],
    )

    result = await app_db_session.execute(
        text("delete from dossiers where id = :dossier_id returning id"),
        {"dossier_id": second_tenant["dossier"]["id"]},
    )
    assert result.first() is None


async def test_association_tables_do_not_leak(app_db_session, client, seed_data, second_tenant):
    create_resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "assoc.user@example.com",
            "password": "TestPass123",
            "first_name": "Assoc",
            "last_name": "User",
            "role_name": "Collaborateur",
        },
        headers=seed_data["headers"],
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    await apply_rls_context(
        app_db_session,
        seed_data["tenant"]["id"],
        seed_data["user"]["id"],
    )
    own_role_result = await app_db_session.execute(
        text("select role_id from user_roles where user_id = :user_id"),
        {"user_id": user_id},
    )
    role_id = own_role_result.scalar_one()

    await apply_rls_context(
        app_db_session,
        second_tenant["tenant"]["id"],
        second_tenant["user"]["id"],
    )
    user_roles_result = await app_db_session.execute(
        text("select user_id from user_roles where user_id = :user_id"),
        {"user_id": user_id},
    )
    role_permissions_result = await app_db_session.execute(
        text("select role_id from role_permissions where role_id = :role_id"),
        {"role_id": role_id},
    )

    assert user_roles_result.first() is None
    assert role_permissions_result.first() is None


async def test_backend_permissions_are_enforced(client, seed_data):
    create_resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "collab@example.com",
            "password": "TestPass123",
            "first_name": "Collab",
            "last_name": "User",
            "role_name": "Collaborateur",
        },
    )
    assert create_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "collab@example.com", "password": "TestPass123"},
    )
    assert login_resp.status_code == 200
    collab_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    forbidden_resp = await client.post(
        "/api/v1/auth/users",
        headers=collab_headers,
        json={
            "email": "nope@example.com",
            "password": "TestPass123",
            "first_name": "No",
            "last_name": "Permission",
            "role_name": "Collaborateur",
        },
    )
    assert forbidden_resp.status_code == 403

    allowed_resp = await client.post(
        "/api/v1/accounting/accounts",
        headers=collab_headers,
        json={
            "dossier_id": seed_data["dossier"]["id"],
            "number": "6129",
            "label": "Charge collab",
            "account_class": 6,
            "nature": "debit",
        },
    )
    assert allowed_resp.status_code == 201


async def test_every_tenant_table_has_rls_and_policy(owner_engine):
    async with owner_engine.connect() as conn:
        tenant_tables_result = await conn.execute(
            text(
                """
                select table_name
                from information_schema.columns
                where table_schema = 'public' and column_name = 'tenant_id'
                """
            )
        )
        tenant_tables = {row[0] for row in tenant_tables_result}

        rls_result = await conn.execute(
            text(
                """
                select c.relname, c.relrowsecurity
                from pg_class c
                join pg_namespace n on n.oid = c.relnamespace
                where n.nspname = 'public'
                  and c.relkind = 'r'
                """
            )
        )
        rls_by_table = {row[0]: row[1] for row in rls_result}

        policy_result = await conn.execute(
            text(
                """
                select tablename, count(*)
                from pg_policies
                where schemaname = 'public'
                group by tablename
                """
            )
        )
        policy_counts = {row[0]: row[1] for row in policy_result}

    assert tenant_tables == RLS_TABLES
    for table_name in RLS_TABLES:
        assert rls_by_table.get(table_name) is True
        assert policy_counts.get(table_name, 0) >= 2
