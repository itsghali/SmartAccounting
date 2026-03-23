"""Tests for dashboard stats and reporting endpoints."""

import uuid


async def test_dashboard_stats(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.get(f"/api/v1/accounting/dashboard-stats?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()

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

    assert isinstance(data["accounts_count"], int)
    assert data["accounts_count"] >= 0
    assert isinstance(data["periods_count"], int)
    assert data["periods_count"] >= 0


async def test_dashboard_stats_with_data(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

    await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "Exercice dashboard",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )

    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "7000",
            "label": "Produits test",
            "account_class": 7,
            "nature": "credit",
        },
    )

    resp = await client.get(f"/api/v1/accounting/dashboard-stats?dossier_id={dossier_id}")
    data = resp.json()
    assert data["accounts_count"] >= 1
    assert data["fiscal_years_count"] >= 1
    assert data["periods_count"] == 13
    assert data["open_periods_count"] == 13


async def test_dashboard_stats_invalid_dossier_returns_404(client, seed_data):
    invalid_dossier_id = uuid.uuid4()
    resp = await client.get(
        f"/api/v1/accounting/dashboard-stats?dossier_id={invalid_dossier_id}"
    )
    assert resp.status_code == 404


async def test_balance_generale_empty(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.get(f"/api/v1/reporting/balance-generale?dossier_id={dossier_id}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_grand_livre_empty(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.get(f"/api/v1/reporting/grand-livre?dossier_id={dossier_id}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_bilan_empty(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.get(f"/api/v1/reporting/bilan?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "actif" in data
    assert "passif" in data
    assert "total_actif" in data["actif"]
    assert "total_passif" in data["passif"]


async def test_cpc_empty(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])
    resp = await client.get(f"/api/v1/reporting/cpc?dossier_id={dossier_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "resultat_exploitation" in data
    assert "resultat_financier" in data
    assert "resultat_courant" in data
    assert "resultat_non_courant" in data
    assert "resultat_net" in data


async def test_balance_with_validated_entry(client, seed_data, future_fiscal_year_dates):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "FY Balance Test",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods = (await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")).json()
    period = periods[0]

    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "6115",
            "label": "Achats bal test",
            "account_class": 6,
            "nature": "debit",
        },
    )
    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "4415X",
            "label": "Fourn bal test",
            "account_class": 4,
            "nature": "credit",
        },
    )
    acc_list = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    achat_id = next(a["id"] for a in acc_list if a["number"] == "6115")
    fourn_id = next(a["id"] for a in acc_list if a["number"] == "4415X")

    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    j = journals[0]

    entry = (
        await client.post(
            "/api/v1/accounting/entries",
            json={
                "dossier_id": dossier_id,
                "journal_id": j["id"],
                "period_id": period["id"],
                "entry_date": future_fiscal_year_dates["second_entry_date"],
                "label": "Achat test balance",
                "lines": [
                    {
                        "account_id": achat_id,
                        "label": "Achats",
                        "debit": "5000.00",
                        "credit": "0.00",
                    },
                    {
                        "account_id": fourn_id,
                        "label": "Fournisseur",
                        "debit": "0.00",
                        "credit": "5000.00",
                    },
                ],
            },
        )
    ).json()

    await client.post(f"/api/v1/accounting/entries/{entry['id']}/validate")

    balance = (
        await client.get(
            f"/api/v1/reporting/balance-generale?dossier_id={dossier_id}"
        )
    ).json()
    assert len(balance) >= 2

    achat_line = next((b for b in balance if b["account_number"] == "6115"), None)
    fourn_line = next((b for b in balance if b["account_number"] == "4415X"), None)
    assert achat_line is not None
    assert fourn_line is not None
    assert achat_line["total_debit"] == "5000.00"
    assert fourn_line["total_credit"] == "5000.00"

    cpc = (
        await client.get(
            f"/api/v1/reporting/cpc?dossier_id={dossier_id}&fiscal_year_id={fy['id']}"
        )
    ).json()
    assert cpc["total_charges_exploitation"] == "5000.00"
    assert cpc["resultat_exploitation"] == "-5000.00"


async def test_cpc_uses_signed_amounts_for_products(
    client, seed_data, future_fiscal_year_dates
):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "FY CPC signed",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods = (await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")).json()
    period = periods[0]
    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    journal = next(j for j in journals if j["code"] == "VT")

    await client.post(
        "/api/v1/accounting/accounts",
        json={
            "dossier_id": dossier_id,
            "number": "3421X",
            "label": "Client CPC",
            "account_class": 3,
            "nature": "debit",
            "is_lettrable": True,
        },
    )
    accounts = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    client_account_id = next(a["id"] for a in accounts if a["number"] == "3421X")
    sales_account_id = next(a["id"] for a in accounts if a["number"] == "7111")
    discount_account_id = next(a["id"] for a in accounts if a["number"] == "7119")

    sale_entry = (
        await client.post(
            "/api/v1/accounting/entries",
            json={
                "dossier_id": dossier_id,
                "journal_id": journal["id"],
                "period_id": period["id"],
                "entry_date": future_fiscal_year_dates["entry_date"],
                "label": "Vente CPC",
                "lines": [
                    {
                        "account_id": client_account_id,
                        "label": "Client",
                        "debit": "1000.00",
                        "credit": "0.00",
                    },
                    {
                        "account_id": sales_account_id,
                        "label": "Vente",
                        "debit": "0.00",
                        "credit": "1000.00",
                    },
                ],
            },
        )
    ).json()
    await client.post(f"/api/v1/accounting/entries/{sale_entry['id']}/validate")

    discount_entry = (
        await client.post(
            "/api/v1/accounting/entries",
            json={
                "dossier_id": dossier_id,
                "journal_id": journal["id"],
                "period_id": period["id"],
                "entry_date": future_fiscal_year_dates["second_entry_date"],
                "label": "RRR CPC",
                "lines": [
                    {
                        "account_id": discount_account_id,
                        "label": "RRR",
                        "debit": "100.00",
                        "credit": "0.00",
                    },
                    {
                        "account_id": client_account_id,
                        "label": "Client",
                        "debit": "0.00",
                        "credit": "100.00",
                    },
                ],
            },
        )
    ).json()
    await client.post(f"/api/v1/accounting/entries/{discount_entry['id']}/validate")

    cpc = (
        await client.get(
            f"/api/v1/reporting/cpc?dossier_id={dossier_id}&fiscal_year_id={fy['id']}"
        )
    ).json()
    assert cpc["total_produits_exploitation"] == "900.00"
    assert cpc["resultat_exploitation"] == "900.00"
    assert cpc["diagnostic_message"] is None


async def test_cpc_explains_when_only_non_cpc_accounts_move(
    client, seed_data, future_fiscal_year_dates
):
    dossier_id = str(seed_data["dossier"]["id"])

    fy_resp = await client.post(
        "/api/v1/core/fiscal-years",
        json={
            "dossier_id": dossier_id,
            "name": "FY CPC diagnostic",
            "start_date": future_fiscal_year_dates["start_date"],
            "end_date": future_fiscal_year_dates["end_date"],
        },
    )
    fy = fy_resp.json()

    periods = (await client.get(f"/api/v1/core/fiscal-years/{fy['id']}/periods")).json()
    period = periods[0]
    journals = (await client.get(f"/api/v1/accounting/journals?dossier_id={dossier_id}")).json()
    journal = next(j for j in journals if j["code"] == "OD")
    accounts = (await client.get(f"/api/v1/accounting/accounts?dossier_id={dossier_id}")).json()
    capital_account_id = next(a["id"] for a in accounts if a["number"] == "1117")
    research_account_id = next(a["id"] for a in accounts if a["number"] == "2121")

    entry = (
        await client.post(
            "/api/v1/accounting/entries",
            json={
                "dossier_id": dossier_id,
                "journal_id": journal["id"],
                "period_id": period["id"],
                "entry_date": future_fiscal_year_dates["entry_date"],
                "label": "Mouvement hors CPC",
                "lines": [
                    {
                        "account_id": research_account_id,
                        "label": "Immobilisation",
                        "debit": "7800.00",
                        "credit": "0.00",
                    },
                    {
                        "account_id": capital_account_id,
                        "label": "Capital",
                        "debit": "0.00",
                        "credit": "7800.00",
                    },
                ],
            },
        )
    ).json()
    await client.post(f"/api/v1/accounting/entries/{entry['id']}/validate")

    cpc = (
        await client.get(
            f"/api/v1/reporting/cpc?dossier_id={dossier_id}&fiscal_year_id={fy['id']}"
        )
    ).json()
    assert cpc["total_produits_exploitation"] == "0.00"
    assert cpc["total_charges_exploitation"] == "0.00"
    assert cpc["eligible_accounts_count"] == 0
    assert cpc["non_cpc_accounts_count"] >= 1
    assert "hors cpc" in cpc["diagnostic_message"].lower()


async def test_seed_defaults_idempotent(client, seed_data):
    dossier_id = str(seed_data["dossier"]["id"])

    resp1 = await client.post(f"/api/v1/accounting/seed-defaults?dossier_id={dossier_id}")
    assert resp1.status_code == 200

    resp2 = await client.post(f"/api/v1/accounting/seed-defaults?dossier_id={dossier_id}")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["accounts_seeded"] == 0
    assert data["journals_seeded"] == 0
