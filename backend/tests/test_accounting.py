import pytest
import pytest_asyncio
from decimal import Decimal


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_fiscal_year(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.post("/api/v1/core/fiscal-years", json={
        "dossier_id": dossier_id,
        "name": "Exercice 2026",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "OPEN"
    assert data["name"] == "Exercice 2026"


@pytest.mark.asyncio
async def test_create_account(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id,
        "number": "6111",
        "label": "Achats de marchandises",
        "account_class": 6,
        "nature": "debit",
    })
    assert resp.status_code == 201
    assert resp.json()["number"] == "6111"


@pytest.mark.asyncio
async def test_create_journal(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)
    resp = await client.post("/api/v1/accounting/journals", json={
        "dossier_id": dossier_id,
        "code": "AC",
        "label": "Journal des achats",
        "journal_type": "achat",
    })
    assert resp.status_code == 201
    assert resp.json()["code"] == "AC"


@pytest.mark.asyncio
async def test_create_balanced_entry(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)

    # Create fiscal year
    fy_resp = await client.post("/api/v1/core/fiscal-years", json={
        "dossier_id": dossier_id,
        "name": "FY 2026",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    })
    fy = fy_resp.json()

    # Get periods
    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    period = periods_resp.json()[0]

    # Create accounts
    await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id, "number": "6110", "label": "Achats",
        "account_class": 6, "nature": "debit",
    })
    acc1 = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()

    await client.post("/api/v1/accounting/accounts", json={
        "dossier_id": dossier_id, "number": "4411", "label": "Fournisseurs",
        "account_class": 4, "nature": "credit",
    })
    acc_list = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()

    achat_id = next(a["id"] for a in acc_list if a["number"] == "6110")
    fournisseur_id = next(a["id"] for a in acc_list if a["number"] == "4411")

    # Create journal
    j_resp = await client.post("/api/v1/accounting/journals", json={
        "dossier_id": dossier_id, "code": "ACH", "label": "Achats",
        "journal_type": "achat",
    })
    journal = j_resp.json()

    # Create balanced entry
    entry_resp = await client.post("/api/v1/accounting/entries", json={
        "dossier_id": dossier_id,
        "journal_id": journal["id"],
        "period_id": period["id"],
        "entry_date": "2026-01-15",
        "label": "Achat marchandises",
        "lines": [
            {"account_id": achat_id, "label": "Achats marchandises", "debit": "10000.00", "credit": "0.00"},
            {"account_id": fournisseur_id, "label": "Fournisseur X", "debit": "0.00", "credit": "10000.00"},
        ],
    })
    assert entry_resp.status_code == 201
    entry = entry_resp.json()
    assert entry["status"] == "DRAFT"
    assert entry["total_debit"] == "10000.00"
    assert entry["total_credit"] == "10000.00"


@pytest.mark.asyncio
async def test_unbalanced_entry_rejected(client, seed_data):
    dossier_id = str(seed_data["dossier"].id)

    fy_resp = await client.post("/api/v1/core/fiscal-years", json={
        "dossier_id": dossier_id,
        "name": "FY Unbal",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    })
    # This will fail because a FY already exists for this dossier if previous test ran,
    # so we handle both cases
    if fy_resp.status_code != 201:
        fy_list = (await client.get(f"/api/v1/core/fiscal-years?dossier_id={dossier_id}")).json()
        fy = fy_list[0]
    else:
        fy = fy_resp.json()

    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    period = periods_resp.json()[0]

    acc_list = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    if len(acc_list) < 2:
        await client.post("/api/v1/accounting/accounts", json={
            "dossier_id": dossier_id, "number": "6120", "label": "Achats 2",
            "account_class": 6, "nature": "debit",
        })
        await client.post("/api/v1/accounting/accounts", json={
            "dossier_id": dossier_id, "number": "4412", "label": "Fourn 2",
            "account_class": 4, "nature": "credit",
        })
        acc_list = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()

    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    if not journals:
        j_resp = await client.post("/api/v1/accounting/journals", json={
            "dossier_id": dossier_id, "code": "OD", "label": "OD", "journal_type": "od",
        })
        journal = j_resp.json()
    else:
        journal = journals[0]

    entry_resp = await client.post("/api/v1/accounting/entries", json={
        "dossier_id": dossier_id,
        "journal_id": journal["id"],
        "period_id": period["id"],
        "entry_date": "2026-01-15",
        "label": "Unbalanced",
        "lines": [
            {"account_id": acc_list[0]["id"], "label": "Line 1", "debit": "500.00", "credit": "0.00"},
            {"account_id": acc_list[1]["id"], "label": "Line 2", "debit": "0.00", "credit": "300.00"},
        ],
    })
    assert entry_resp.status_code == 400
    assert "balanced" in entry_resp.json()["detail"].lower()
