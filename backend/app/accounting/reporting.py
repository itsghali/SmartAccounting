"""
Reporting services: Balance Generale, Grand Livre, Bilan, CPC.
All reports filter by tenant_id, dossier_id, and optionally by period/fiscal year.
"""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.models import Account, JournalEntry, JournalEntryLine
from app.core.models import AccountingPeriod, FiscalYear


# ──────────────────── Balance Generale ────────────────────


async def get_balance_generale(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dossier_id: uuid.UUID,
    fiscal_year_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    validated_only: bool = True,
) -> list[dict]:
    """
    Balance generale: pour chaque compte, total debit, total credit, solde.
    Only includes accounts that have at least one movement.
    """
    # Base conditions for entries
    entry_conditions = [
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.dossier_id == dossier_id,
    ]
    if validated_only:
        entry_conditions.append(JournalEntry.status == "VALIDATED")

    if period_id:
        entry_conditions.append(JournalEntry.period_id == period_id)
    elif fiscal_year_id:
        # Get all periods for this fiscal year
        entry_conditions.append(
            JournalEntry.period_id.in_(
                select(AccountingPeriod.id).where(
                    AccountingPeriod.fiscal_year_id == fiscal_year_id
                )
            )
        )

    query = (
        select(
            Account.number,
            Account.label,
            Account.account_class,
            Account.nature,
            func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0.00")).label("total_debit"),
            func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0.00")).label("total_credit"),
        )
        .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
        .join(JournalEntry, JournalEntryLine.entry_id == JournalEntry.id)
        .where(
            Account.tenant_id == tenant_id,
            Account.dossier_id == dossier_id,
            *entry_conditions,
        )
        .group_by(Account.number, Account.label, Account.account_class, Account.nature)
        .order_by(Account.number)
    )

    result = await db.execute(query)
    rows = result.all()

    balance = []
    grand_total_debit = Decimal("0.00")
    grand_total_credit = Decimal("0.00")

    for row in rows:
        total_debit = row.total_debit
        total_credit = row.total_credit
        solde_debiteur = max(total_debit - total_credit, Decimal("0.00"))
        solde_crediteur = max(total_credit - total_debit, Decimal("0.00"))

        grand_total_debit += total_debit
        grand_total_credit += total_credit

        balance.append({
            "account_number": row.number,
            "account_label": row.label,
            "account_class": row.account_class,
            "nature": row.nature,
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
            "solde_debiteur": str(solde_debiteur),
            "solde_crediteur": str(solde_crediteur),
        })

    return balance


# ──────────────────── Grand Livre ────────────────────


async def get_grand_livre(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dossier_id: uuid.UUID,
    account_number: str | None = None,
    fiscal_year_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    validated_only: bool = True,
) -> list[dict]:
    """
    Grand livre: detail des mouvements par compte.
    Returns accounts with their individual entry lines.
    """
    entry_conditions = [
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.dossier_id == dossier_id,
    ]
    if validated_only:
        entry_conditions.append(JournalEntry.status == "VALIDATED")

    if period_id:
        entry_conditions.append(JournalEntry.period_id == period_id)
    elif fiscal_year_id:
        entry_conditions.append(
            JournalEntry.period_id.in_(
                select(AccountingPeriod.id).where(
                    AccountingPeriod.fiscal_year_id == fiscal_year_id
                )
            )
        )

    account_conditions = [
        Account.tenant_id == tenant_id,
        Account.dossier_id == dossier_id,
    ]
    if account_number:
        account_conditions.append(Account.number == account_number)

    query = (
        select(
            Account.number,
            Account.label.label("account_label"),
            JournalEntry.entry_date,
            JournalEntry.piece_number,
            JournalEntry.label.label("entry_label"),
            JournalEntryLine.debit,
            JournalEntryLine.credit,
            JournalEntryLine.lettrage_code,
        )
        .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
        .join(JournalEntry, JournalEntryLine.entry_id == JournalEntry.id)
        .where(
            *account_conditions,
            *entry_conditions,
        )
        .order_by(Account.number, JournalEntry.entry_date, JournalEntry.piece_number)
    )

    result = await db.execute(query)
    rows = result.all()

    # Group by account
    accounts_dict: dict[str, dict] = {}
    for row in rows:
        key = row.number
        if key not in accounts_dict:
            accounts_dict[key] = {
                "account_number": row.number,
                "account_label": row.account_label,
                "lines": [],
                "total_debit": Decimal("0.00"),
                "total_credit": Decimal("0.00"),
            }

        accounts_dict[key]["lines"].append({
            "date": str(row.entry_date),
            "piece_number": row.piece_number,
            "label": row.entry_label,
            "debit": str(row.debit),
            "credit": str(row.credit),
            "lettrage_code": row.lettrage_code,
        })
        accounts_dict[key]["total_debit"] += row.debit
        accounts_dict[key]["total_credit"] += row.credit

    # Convert to list and stringify decimals
    grand_livre = []
    for acct in accounts_dict.values():
        solde = acct["total_debit"] - acct["total_credit"]
        grand_livre.append({
            "account_number": acct["account_number"],
            "account_label": acct["account_label"],
            "lines": acct["lines"],
            "total_debit": str(acct["total_debit"]),
            "total_credit": str(acct["total_credit"]),
            "solde": str(solde),
        })

    return grand_livre


# ──────────────────── Bilan ────────────────────


# Mapping PCM classes to Bilan sections
BILAN_ACTIF_CLASSES = [2, 3, 5]  # Immobilise + Circulant + Tresorerie
BILAN_PASSIF_CLASSES = [1, 4]     # Financement permanent + Passif circulant


async def get_bilan(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dossier_id: uuid.UUID,
    fiscal_year_id: uuid.UUID | None = None,
    validated_only: bool = True,
) -> dict:
    """
    Bilan simplifie: actif (classes 2,3,5) vs passif (classes 1,4) + resultat.
    """
    balance = await get_balance_generale(
        db, tenant_id, dossier_id, fiscal_year_id=fiscal_year_id,
        validated_only=validated_only,
    )

    actif_immobilise = []
    actif_circulant = []
    tresorerie_actif = []
    financement_permanent = []
    passif_circulant = []
    tresorerie_passif = []

    for line in balance:
        cls = line["account_class"]
        solde_d = Decimal(line["solde_debiteur"])
        solde_c = Decimal(line["solde_crediteur"])

        entry = {
            "account_number": line["account_number"],
            "account_label": line["account_label"],
            "montant": str(solde_d if solde_d > 0 else solde_c),
        }

        if cls == 2:
            actif_immobilise.append(entry)
        elif cls == 3:
            actif_circulant.append(entry)
        elif cls == 5:
            if solde_d > 0:
                tresorerie_actif.append(entry)
            else:
                tresorerie_passif.append(entry)
        elif cls == 1:
            financement_permanent.append(entry)
        elif cls == 4:
            passif_circulant.append(entry)

    def total_section(section: list[dict]) -> str:
        return str(sum(Decimal(e["montant"]) for e in section))

    total_actif = str(
        Decimal(total_section(actif_immobilise))
        + Decimal(total_section(actif_circulant))
        + Decimal(total_section(tresorerie_actif))
    )
    total_passif = str(
        Decimal(total_section(financement_permanent))
        + Decimal(total_section(passif_circulant))
        + Decimal(total_section(tresorerie_passif))
    )

    return {
        "actif": {
            "actif_immobilise": actif_immobilise,
            "actif_circulant": actif_circulant,
            "tresorerie_actif": tresorerie_actif,
            "total_actif_immobilise": total_section(actif_immobilise),
            "total_actif_circulant": total_section(actif_circulant),
            "total_tresorerie_actif": total_section(tresorerie_actif),
            "total_actif": total_actif,
        },
        "passif": {
            "financement_permanent": financement_permanent,
            "passif_circulant": passif_circulant,
            "tresorerie_passif": tresorerie_passif,
            "total_financement_permanent": total_section(financement_permanent),
            "total_passif_circulant": total_section(passif_circulant),
            "total_tresorerie_passif": total_section(tresorerie_passif),
            "total_passif": total_passif,
        },
    }


# ──────────────────── CPC ────────────────────


async def get_cpc(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dossier_id: uuid.UUID,
    fiscal_year_id: uuid.UUID | None = None,
    validated_only: bool = True,
) -> dict:
    """
    Compte de Produits et Charges (CPC) marocain.
    Classes 6 (charges) et 7 (produits), avec resultat d'exploitation,
    resultat financier, resultat courant, resultat non courant, resultat net.
    """
    balance = await get_balance_generale(
        db, tenant_id, dossier_id, fiscal_year_id=fiscal_year_id,
        validated_only=validated_only,
    )

    # Categorize by CPC sections based on PCM sub-classes
    charges_exploitation = []   # 61xx
    charges_financieres = []    # 63xx
    charges_non_courantes = []  # 65xx
    impots_sur_resultats = []   # 67xx
    produits_exploitation = []  # 71xx
    produits_financiers = []    # 73xx
    produits_non_courants = []  # 75xx

    for line in balance:
        num = line["account_number"]
        solde_d = Decimal(line["solde_debiteur"])
        solde_c = Decimal(line["solde_crediteur"])
        montant = solde_d if solde_d > 0 else solde_c

        entry = {
            "account_number": num,
            "account_label": line["account_label"],
            "montant": str(montant),
        }

        if num.startswith("61") or num.startswith("62"):
            charges_exploitation.append(entry)
        elif num.startswith("63") or num.startswith("64"):
            charges_financieres.append(entry)
        elif num.startswith("65") or num.startswith("66"):
            charges_non_courantes.append(entry)
        elif num.startswith("67"):
            impots_sur_resultats.append(entry)
        elif num.startswith("71") or num.startswith("72"):
            produits_exploitation.append(entry)
        elif num.startswith("73") or num.startswith("74"):
            produits_financiers.append(entry)
        elif num.startswith("75") or num.startswith("76"):
            produits_non_courants.append(entry)

    def total_section(section: list[dict]) -> Decimal:
        return sum(Decimal(e["montant"]) for e in section)

    t_charges_exploit = total_section(charges_exploitation)
    t_produits_exploit = total_section(produits_exploitation)
    resultat_exploitation = t_produits_exploit - t_charges_exploit

    t_charges_fin = total_section(charges_financieres)
    t_produits_fin = total_section(produits_financiers)
    resultat_financier = t_produits_fin - t_charges_fin

    resultat_courant = resultat_exploitation + resultat_financier

    t_charges_nc = total_section(charges_non_courantes)
    t_produits_nc = total_section(produits_non_courants)
    resultat_non_courant = t_produits_nc - t_charges_nc

    t_impots = total_section(impots_sur_resultats)
    resultat_avant_impots = resultat_courant + resultat_non_courant
    resultat_net = resultat_avant_impots - t_impots

    return {
        "produits_exploitation": [e for e in produits_exploitation],
        "charges_exploitation": [e for e in charges_exploitation],
        "total_produits_exploitation": str(t_produits_exploit),
        "total_charges_exploitation": str(t_charges_exploit),
        "resultat_exploitation": str(resultat_exploitation),
        "produits_financiers": [e for e in produits_financiers],
        "charges_financieres": [e for e in charges_financieres],
        "total_produits_financiers": str(t_produits_fin),
        "total_charges_financieres": str(t_charges_fin),
        "resultat_financier": str(resultat_financier),
        "resultat_courant": str(resultat_courant),
        "produits_non_courants": [e for e in produits_non_courants],
        "charges_non_courantes": [e for e in charges_non_courantes],
        "total_produits_non_courants": str(t_produits_nc),
        "total_charges_non_courantes": str(t_charges_nc),
        "resultat_non_courant": str(resultat_non_courant),
        "impots_sur_resultats": str(t_impots),
        "resultat_avant_impots": str(resultat_avant_impots),
        "resultat_net": str(resultat_net),
    }
