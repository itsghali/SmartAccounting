import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_fiscal_year(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": f"Exercice {future_fiscal_year_dates['year']}",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "OPEN"
    assert data["name"] == f"Exercice {future_fiscal_year_dates['year']}"


@pytest.mark.asyncio
async def test_create_fiscal_year_rejects_past_dates(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    next_month = (date.today() + timedelta(days=30)).isoformat()

    resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "Exercice invalide",
            "start_date": yesterday,
            "end_date": next_month,
        },
    )
    assert resp.status_code == 400
    assert "date de debut" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_account(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "6111A",
            "label": "Achats de marchandises",
            "account_class": 6,
            "nature": "debit",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["number"] == "6111A"


@pytest.mark.asyncio
async def test_create_journal(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.post(
        "/api/v1/accounting/journals",
        json={
            "dossier_id": dossier_id,
            "code": "ACH",
            "label": "Journal des achats",
            "journal_type": "achat",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["code"] == "ACH"


@pytest.mark.asyncio
async def test_create_balanced_entry(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": f"FY {future_fiscal_year_dates['year']}",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    period = periods_resp.json()[0]

    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "6110",
            "label": "Achats",
            "account_class": 6,
            "nature": "debit",
        },
    )
    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "4411X",
            "label": "Fournisseurs",
            "account_class": 4,
            "nature": "credit",
        },
    )
    acc_list = (
        await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")
    ).json()

    achat_id = next(a["id"] for a in acc_list if a["number"] == "6110")
    fournisseur_id = next(a["id"] for a in acc_list if a["number"] == "4411X")

    j_resp = await client.post(
        "/api/v1/accounting/journals",
        json={
            "dossier_id": dossier_id,
            "code": "ACH2",
            "label": "Achats",
            "journal_type": "achat",
        },
    )
    journal = j_resp.json()

    entry_resp = await client.post(
        "/api/v1/accounting/entries",
        json={
            "dossier_id": dossier_id,
            "journal_id": journal["id"],
            "period_id": period["id"],
            "entry_date": future_fiscal_year_dates["entry_date"],
            "label": "Achat marchandises",
            "lines": [
                {
                    "account_id": achat_id,
                    "label": "Achats marchandises",
                    "debit": "10000.00",
                    "credit": "0.00",
                },
                {
                    "account_id": fournisseur_id,
                    "label": "Fournisseur X",
                    "debit": "0.00",
                    "credit": "10000.00",
                },
            ],
        },
    )
    assert entry_resp.status_code == 201
    entry = entry_resp.json()
    assert entry["status"] == "DRAFT"
    assert entry["total_debit"] == "10000.00"
    assert entry["total_credit"] == "10000.00"


@pytest.mark.asyncio
async def test_unbalanced_entry_rejected(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "FY Unbal",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    period = periods_resp.json()[0]

    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "6120",
            "label": "Achats 2",
            "account_class": 6,
            "nature": "debit",
        },
    )
    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "4412X",
            "label": "Fourn 2",
            "account_class": 4,
            "nature": "credit",
        },
    )
    acc_list = (
        await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")
    ).json()

    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    journal = journals[0]

    entry_resp = await client.post(
        "/api/v1/accounting/entries",
        json={
            "dossier_id": dossier_id,
            "journal_id": journal["id"],
            "period_id": period["id"],
            "entry_date": future_fiscal_year_dates["entry_date"],
            "label": "Unbalanced",
            "lines": [
                {
                    "account_id": acc_list[0]["id"],
                    "label": "Line 1",
                    "debit": "500.00",
                    "credit": "0.00",
                },
                {
                    "account_id": acc_list[1]["id"],
                    "label": "Line 2",
                    "debit": "0.00",
                    "credit": "300.00",
                },
            ],
        },
    )
    assert entry_resp.status_code == 400
    assert "balanced" in entry_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_entry_rejects_past_business_date(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": f"FY {future_fiscal_year_dates['year']} dates",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    period = periods_resp.json()[0]
    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    accounts = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    debit_account = next(account for account in accounts if account["number"] == "6111")
    credit_account = next(account for account in accounts if account["number"] == "4411")
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    resp = await client.post(
        "/api/v1/accounting/entries",
        json={
            "dossier_id": dossier_id,
            "journal_id": journals[0]["id"],
            "period_id": period["id"],
            "entry_date": yesterday,
            "label": "Date passee",
            "lines": [
                {
                    "account_id": debit_account["id"],
                    "label": "Charge",
                    "debit": "100.00",
                    "credit": "0.00",
                },
                {
                    "account_id": credit_account["id"],
                    "label": "Fournisseur",
                    "debit": "0.00",
                    "credit": "100.00",
                },
            ],
        },
    )

    assert resp.status_code == 400
    assert "date d'ecriture" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_entry_date_must_belong_to_selected_period(
    client, seed_data, future_fiscal_year_dates
):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": f"FY {future_fiscal_year_dates['year']} scope",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods_resp = await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")
    periods = periods_resp.json()
    january_period = periods[0]
    february_period = periods[1]
    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    accounts = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    debit_account = next(account for account in accounts if account["number"] == "6111")
    credit_account = next(account for account in accounts if account["number"] == "4411")

    resp = await client.post(
        "/api/v1/accounting/entries",
        json={
            "dossier_id": dossier_id,
            "journal_id": journals[0]["id"],
            "period_id": january_period["id"],
            "entry_date": february_period["start_date"],
            "label": "Periode incoherente",
            "lines": [
                {
                    "account_id": debit_account["id"],
                    "label": "Charge",
                    "debit": "100.00",
                    "credit": "0.00",
                },
                {
                    "account_id": credit_account["id"],
                    "label": "Fournisseur",
                    "debit": "0.00",
                    "credit": "100.00",
                },
            ],
        },
    )

    assert resp.status_code == 400
    assert "periode selectionnee" in resp.json()["detail"].lower()
