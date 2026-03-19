"""Tests for dashboard stats and reporting endpoints."""

import uuid

async def test_dashboard_stats(client, seed_data):
    """Dashboard stats endpoint should return all counters."""
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.get(f"/api/v1/accounting/dashboard-stats?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()

    # All expected fields are present
    assert "accounts_count" in data
    assert "journals_count" in data
    assert "entries_count" in data
    assert "draft_entries_count" in data
    assert "validated_entries_count" in data
    assert "fiscal_years_count" in data
    assert "open_fiscal_years_count" in data
    assert "periods_count" in data
    assert "open_periods_count" in data
    assert "locked_periods_count" in data
    assert "third_parties_count" in data
    assert "total_debit" in data
    assert "total_credit" in data

    # All counts are non-negative integers
    assert isinstance(data["accounts_count"], int)
    assert data["accounts_count"] >= 0
    assert isinstance(data["periods_count"], int)
    assert data["periods_count"] >= 0


async def test_dashboard_stats_with_data(client, seed_data):
    """Dashboard stats should reflect created data."""
    dossier_id = str(seed_data["dossier"].id)

    await client.post("/api/v1/core/fiscal-years", json={
        "dossier_id": dossier_id,
        "name": "Exercice dashboard",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    })

    # Create an account
    await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id,
        "number": "7000",
        "label": "Produits test",
        "account_class": 7,
        "nature": "credit",
    })

    resp = await client.get(f"/api/v1/accounting/dashboard-stats?dossier_id={dossier_id}")
    data = resp.json()
    assert data["accounts_count"] >= 1
    assert data["fiscal_years_count"] >= 1
    assert data["periods_count"] == 13
    assert data["open_periods_count"] == 13


async def test_dashboard_stats_invalid_dossier_returns_404(client):
    invalid_dossier_id = uuid.uuid4()
    resp = await client.get(
        f"/api/v1/accounting/dashboard-stats?dossier_id={invalid_dossier_id}"
    )
    assert resp.status_code == 404


async def test_balance_generale_empty(client, seed_data):
    """Balance generale should return empty list when no validated entries."""
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.get(f"/api/v1/reporting/balance-generale?dossier_id={dossier_id}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_grand_livre_empty(client, seed_data):
    """Grand livre should return empty list when no validated entries."""
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.get(f"/api/v1/reporting/grand-livre?dossier_id={dossier_id}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_bilan_empty(client, seed_data):
    """Bilan should return actif/passif structure even when empty."""
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.get(f"/api/v1/reporting/bilan?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "actif" in data
    assert "passif" in data
    assert "total_actif" in data["actif"]
    assert "total_passif" in data["passif"]


async def test_cpc_empty(client, seed_data):
    """CPC should return all result sections even when empty."""
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.get(f"/api/v1/reporting/cpc?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "resultat_exploitation" in data
    assert "resultat_financier" in data
    assert "resultat_courant" in data
    assert "resultat_non_courant" in data
    assert "resultat_net" in data


async def test_balance_with_validated_entry(client, seed_data):
    """Balance should show data after creating and validating an entry."""
    dossier_id = str(seed_data["dossier"].id)

    # Setup: fiscal year + period
    fy_resp = await client.post("/api/v1/core/fiscal-years", json={
        "dossier_id": dossier_id,
        "name": "FY Balance Test",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    })
    if fy_resp.status_code != 201:
        fy_list = (await client.get(f"/api/v1/core/fiscal-years?dossier_id={dossier_id}")).json()
        fy = fy_list[0]
    else:
        fy = fy_resp.json()

    periods = (await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")).json()
    period = periods[0]

    # Create accounts
    await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id, "number": "6115", "label": "Achats bal test",
        "account_class": 6, "nature": "debit",
    })
    await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id, "number": "4415", "label": "Fourn bal test",
        "account_class": 4, "nature": "credit",
    })
    acc_list = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    achat_id = next(a["id"] for a in acc_list if a["number"] == "6115")
    fourn_id = next(a["id"] for a in acc_list if a["number"] == "4415")

    # Create journal
    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    if not journals:
        j = (await client.post("/api/v1/accounting/journals", json={
            "dossier_id": dossier_id, "code": "TB", "label": "Test bal", "journal_type": "od",
        })).json()
    else:
        j = journals[0]

    # Create and validate entry
    entry = (await client.post("/api/v1/accounting/entries", json={
        "dossier_id": dossier_id,
        "journal_id": j["id"],
        "period_id": period["id"],
        "entry_date": "2026-01-20",
        "label": "Achat test balance",
        "lines": [
            {"account_id": achat_id, "label": "Achats", "debit": "5000.00", "credit": "0.00"},
            {"account_id": fourn_id, "label": "Fournisseur", "debit": "0.00", "credit": "5000.00"},
        ],
    })).json()

    # Validate
    await client.post(f"/api/v1/accounting/entries/{entry['id']}/validate")

    # Check balance
    balance = (await client.get(
        f"/api/v1/reporting/balance-generale?dossier_id={dossier_id}"
    )).json()
    assert len(balance) >= 2

    # Find our accounts
    achat_line = next((b for b in balance if b["account_number"] == "6115"), None)
    fourn_line = next((b for b in balance if b["account_number"] == "4415"), None)
    assert achat_line is not None
    assert fourn_line is not None
    assert achat_line["total_debit"] == "5000.00"
    assert fourn_line["total_credit"] == "5000.00"


async def test_seed_defaults_idempotent(client, seed_data):
    """Calling seed-defaults twice should not crash (idempotent)."""
    dossier_id = str(seed_data["dossier"].id)

    # First seed
    resp1 = await client.post(f"/api/v1/accounting/seed-defaults?dossier_id={dossier_id}")
    assert resp1.status_code == 200

    # Second seed should succeed (skip because data exists)
    resp2 = await client.post(f"/api/v1/accounting/seed-defaults?dossier_id={dossier_id}")
    assert resp2.status_code == 200
    data = resp2.json()
    # Second call should seed 0 (skipped)
    assert data["accounts_seeded"] == 0
    assert data["journals_seeded"] == 0
