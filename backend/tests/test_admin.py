async def test_list_roles_exposes_predefined_roles(client, seed_data):
    resp = await client.get("/api/v1/auth/roles")
    assert resp.status_code == 200
    role_names = {role["name"] for role in resp.json()}
    assert "Administrateur" in role_names
    assert "Responsable" in role_names
    assert "Collaborateur" in role_names


async def test_admin_can_create_user(client, seed_data):
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


async def test_responsable_can_create_collaborateur(client, seed_data):
    create_resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "responsable@example.com",
            "password": "TestPass123",
            "first_name": "Resp",
            "last_name": "Onsable",
            "role_name": "Responsable",
        },
    )
    assert create_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "responsable@example.com", "password": "TestPass123"},
    )
    assert login_resp.status_code == 200
    responsable_headers = {
        "Authorization": f"Bearer {login_resp.json()['access_token']}"
    }

    resp = await client.post(
        "/api/v1/auth/users",
        headers=responsable_headers,
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


async def test_responsable_cannot_create_responsable(client, seed_data):
    create_resp = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "responsable.bis@example.com",
            "password": "TestPass123",
            "first_name": "Resp",
            "last_name": "Bis",
            "role_name": "Responsable",
        },
    )
    assert create_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "responsable.bis@example.com", "password": "TestPass123"},
    )
    assert login_resp.status_code == 200
    responsable_headers = {
        "Authorization": f"Bearer {login_resp.json()['access_token']}"
    }

    resp = await client.post(
        "/api/v1/auth/users",
        headers=responsable_headers,
        json={
            "email": "another.responsable@example.com",
            "password": "TestPass123",
            "first_name": "Another",
            "last_name": "Responsable",
            "role_name": "Responsable",
        },
    )
    assert resp.status_code == 400


async def test_delete_dossier_is_logical(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

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
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    assert fiscal_year_resp.status_code == 404
