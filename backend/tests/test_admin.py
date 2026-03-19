from app.auth.models import Role, User, UserRole
from app.auth.security import create_access_token, hash_password


async def test_list_roles_exposes_predefined_roles(client):
    resp = await client.get("/api/v1/auth/roles")
    assert resp.status_code == 200
    role_names = {role["name"] for role in resp.json()}
    assert "Administrateur" in role_names
    assert "Responsable" in role_names
    assert "Collaborateur" in role_names


async def test_admin_can_create_user(client):
    payload = {
        "email": "new.user@example.com",
        "password": "TestPass123",
        "first_name": "New",
        "last_name": "User",
        "role_name": "Responsable",
    }
    resp = await client.post("/api/v1/auth/users", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "Responsable" in data["roles"]


async def test_responsable_can_create_user(client, db_session, seed_data):
    tenant_id = seed_data["tenant"].id

    responsable_role = Role(
        tenant_id=tenant_id,
        name="Responsable",
        description="Gestion des utilisateurs et des dossiers",
        is_system=True,
    )
    db_session.add(responsable_role)
    await db_session.flush()

    responsable_user = User(
        tenant_id=tenant_id,
        email="responsable@example.com",
        password_hash=hash_password("TestPass123"),
        first_name="Resp",
        last_name="Onsable",
        is_active=True,
    )
    db_session.add(responsable_user)
    await db_session.flush()

    db_session.add(UserRole(user_id=responsable_user.id, role_id=responsable_role.id))
    await db_session.commit()

    token = create_access_token(responsable_user.id, tenant_id, "Responsable")
    client.headers["Authorization"] = f"Bearer {token}"

    resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "created.by.responsable@example.com",
            "password": "TestPass123",
            "first_name": "Created",
            "last_name": "By Responsable",
            "role_name": "Collaborateur",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "created.by.responsable@example.com"


async def test_responsable_cannot_create_responsable(client, db_session, seed_data):
    tenant_id = seed_data["tenant"].id

    responsable_role = Role(
        tenant_id=tenant_id,
        name="Responsable",
        description="Gestion des utilisateurs et des dossiers",
        is_system=True,
    )
    db_session.add(responsable_role)
    await db_session.flush()

    responsable_user = User(
        tenant_id=tenant_id,
        email="responsable.bis@example.com",
        password_hash=hash_password("TestPass123"),
        first_name="Resp",
        last_name="Bis",
        is_active=True,
    )
    db_session.add(responsable_user)
    await db_session.flush()

    db_session.add(UserRole(user_id=responsable_user.id, role_id=responsable_role.id))
    await db_session.commit()

    token = create_access_token(responsable_user.id, tenant_id, "Responsable")
    client.headers["Authorization"] = f"Bearer {token}"

    resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "another.responsable@example.com",
            "password": "TestPass123",
            "first_name": "Another",
            "last_name": "Responsable",
            "role_name": "Responsable",
        },
    )
    assert resp.status_code == 400


async def test_delete_dossier_is_logical(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)

    delete_resp = await client.delete(f"/api/v1/tenant/dossiers/{dossier_id}")
    assert delete_resp.status_code == 204

    list_resp = await client.get("/api/v1/tenant/dossiers")
    assert list_resp.status_code == 200
    returned_ids = {dossier["id"] for dossier in list_resp.json()}
    assert dossier_id not in returned_ids

    stats_resp = await client.get(
        f"/api/v1/accounting/dashboard-stats?dossier_id={dossier_id}"
    )
    assert stats_resp.status_code == 404

    account_resp = await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "6111",
            "label": "Achats marchandises",
            "account_class": 6,
            "nature": "debit",
        },
    )
    assert account_resp.status_code == 404

    fiscal_year_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "Exercice supprime",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        },
    )
    assert fiscal_year_resp.status_code == 404
