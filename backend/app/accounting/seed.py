"""
Seed data for Moroccan CGNC / PCM (Plan Comptable Marocain).

This module provides:
- PCM_ACCOUNTS: the standard Moroccan chart of accounts (classes 1-9)
- DEFAULT_JOURNALS: standard journal types for a Moroccan dossier
- seed_dossier_defaults(): seeds both accounts and journals for a new dossier
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.models import Account, Journal

# ──────────────────────────────────────────────────────────────
# Plan Comptable Marocain (PCM / CGNC) — comptes principaux
# Format: (number, label, class, nature, account_type, is_lettrable, parent)
# ──────────────────────────────────────────────────────────────

PCM_ACCOUNTS: list[tuple[str, str, int, str, str, bool, str | None]] = [
    # ═══════ CLASSE 1 — Comptes de financement permanent ═══════
    ("1111", "Capital social", 1, "credit", "detail", False, None),
    ("1117", "Capital personnel", 1, "credit", "detail", False, None),
    ("1140", "Reserves legales", 1, "credit", "detail", False, None),
    ("1150", "Autres reserves", 1, "credit", "detail", False, None),
    ("1161", "Report a nouveau (SC)", 1, "credit", "detail", False, None),
    ("1169", "Report a nouveau (SD)", 1, "debit", "detail", False, None),
    ("1191", "Resultat net de l'exercice (SC)", 1, "credit", "detail", False, None),
    ("1199", "Resultat net de l'exercice (SD)", 1, "debit", "detail", False, None),
    ("1410", "Emprunts obligataires", 1, "credit", "detail", False, None),
    ("1481", "Emprunts aupres des etablissements de credit", 1, "credit", "detail", False, None),
    ("1486", "Fournisseurs d'immobilisations", 1, "credit", "detail", True, None),
    ("1488", "Dettes de financement diverses", 1, "credit", "detail", False, None),
    ("1511", "Provisions pour litiges", 1, "credit", "detail", False, None),
    ("1512", "Provisions pour garanties donnees aux clients", 1, "credit", "detail", False, None),
    ("1555", "Provisions pour charges a repartir sur plusieurs exercices", 1, "credit", "detail", False, None),

    # ═══════ CLASSE 2 — Comptes d'actif immobilise ═══════
    ("2111", "Frais de constitution", 2, "debit", "detail", False, None),
    ("2112", "Frais prealables au demarrage", 2, "debit", "detail", False, None),
    ("2113", "Frais d'augmentation du capital", 2, "debit", "detail", False, None),
    ("2114", "Frais sur operations de fusions/scissions/transformations", 2, "debit", "detail", False, None),
    ("2116", "Frais de prospection", 2, "debit", "detail", False, None),
    ("2117", "Frais de publicite", 2, "debit", "detail", False, None),
    ("2121", "Frais de recherche", 2, "debit", "detail", False, None),
    ("2125", "Frais de developpement", 2, "debit", "detail", False, None),
    ("2210", "Brevets, marques, droits et valeurs similaires", 2, "debit", "detail", False, None),
    ("2220", "Fonds commercial", 2, "debit", "detail", False, None),
    ("2230", "Terrains", 2, "debit", "detail", False, None),
    ("2311", "Terrains nus", 2, "debit", "detail", False, None),
    ("2312", "Terrains amenages", 2, "debit", "detail", False, None),
    ("2313", "Terrains batis", 2, "debit", "detail", False, None),
    ("2321", "Batiments", 2, "debit", "detail", False, None),
    ("2323", "Constructions sur terrains d'autrui", 2, "debit", "detail", False, None),
    ("2325", "Ouvrages d'infrastructure", 2, "debit", "detail", False, None),
    ("2327", "Agencements et amenagements des constructions", 2, "debit", "detail", False, None),
    ("2328", "Autres constructions", 2, "debit", "detail", False, None),
    ("2331", "Installations techniques", 2, "debit", "detail", False, None),
    ("2332", "Materiel et outillage", 2, "debit", "detail", False, None),
    ("2340", "Materiel de transport", 2, "debit", "detail", False, None),
    ("2351", "Mobilier de bureau", 2, "debit", "detail", False, None),
    ("2352", "Materiel de bureau", 2, "debit", "detail", False, None),
    ("2355", "Materiel informatique", 2, "debit", "detail", False, None),
    ("2380", "Autres immobilisations corporelles", 2, "debit", "detail", False, None),
    ("2393", "Immobilisations corporelles en cours", 2, "debit", "detail", False, None),
    ("2397", "Avances et acomptes verses sur commandes d'immob.", 2, "debit", "detail", False, None),
    ("2411", "Prets au personnel", 2, "debit", "detail", True, None),
    ("2418", "Autres prets immobilises", 2, "debit", "detail", True, None),
    ("2481", "Titres de participation", 2, "debit", "detail", False, None),
    ("2486", "Depots et cautionnements verses", 2, "debit", "detail", True, None),
    ("2510", "Titres de participation", 2, "debit", "detail", False, None),
    ("2811", "Amortissement des frais preliminaires", 2, "credit", "detail", False, "2111"),
    ("2831", "Amortissement des installations techniques", 2, "credit", "detail", False, "2331"),
    ("2832", "Amortissement du materiel et outillage", 2, "credit", "detail", False, "2332"),
    ("2834", "Amortissement du materiel de transport", 2, "credit", "detail", False, "2340"),
    ("2835", "Amortissement du mobilier, materiel de bureau et informatique", 2, "credit", "detail", False, "2351"),
    ("2920", "Provisions pour depreciation des immobilisations corporelles", 2, "credit", "detail", False, None),

    # ═══════ CLASSE 3 — Comptes d'actif circulant (HT) ═══════
    ("3111", "Marchandises", 3, "debit", "detail", False, None),
    ("3121", "Matieres premieres", 3, "debit", "detail", False, None),
    ("3122", "Matieres et fournitures consommables", 3, "debit", "detail", False, None),
    ("3123", "Emballages", 3, "debit", "detail", False, None),
    ("3131", "Produits en cours", 3, "debit", "detail", False, None),
    ("3141", "Produits intermediaires", 3, "debit", "detail", False, None),
    ("3145", "Produits finis", 3, "debit", "detail", False, None),
    ("3149", "Produits residuels (dechets et rebuts)", 3, "debit", "detail", False, None),
    ("3411", "Fournisseurs, avances et acomptes verses", 3, "debit", "detail", True, None),
    ("3421", "Clients", 3, "debit", "detail", True, None),
    ("3423", "Clients — retenues de garantie", 3, "debit", "detail", True, None),
    ("3424", "Clients douteux ou litigieux", 3, "debit", "detail", True, None),
    ("3425", "Clients — effets a recevoir", 3, "debit", "detail", True, None),
    ("3427", "RRR a obtenir — avoirs non encore recus", 3, "debit", "detail", True, None),
    ("3431", "Avances et acomptes au personnel", 3, "debit", "detail", True, None),
    ("3441", "Etat — subventions a recevoir", 3, "debit", "detail", False, None),
    ("3443", "Etat — acomptes sur impots sur les resultats", 3, "debit", "detail", False, None),
    ("3445", "Etat — TVA recuperable", 3, "debit", "detail", False, None),
    ("34451", "Etat — TVA recuperable sur immobilisations", 3, "debit", "detail", False, "3445"),
    ("34452", "Etat — TVA recuperable sur charges", 3, "debit", "detail", False, "3445"),
    ("3448", "Autres comptes debiteurs de l'Etat", 3, "debit", "detail", False, None),
    ("3450", "Comptes d'associes debiteurs", 3, "debit", "detail", True, None),
    ("3458", "Etat — comptes transitoires ou d'attente", 3, "debit", "detail", False, None),
    ("3461", "Autres debiteurs", 3, "debit", "detail", True, None),
    ("3491", "Charges constatees d'avance", 3, "debit", "detail", False, None),
    ("3493", "Interets courus et non echus a percevoir", 3, "debit", "detail", False, None),
    ("3497", "Comptes de repartition periodique des charges", 3, "debit", "detail", False, None),

    # ═══════ CLASSE 4 — Comptes de passif circulant (HT) ═══════
    ("4411", "Fournisseurs", 4, "credit", "detail", True, None),
    ("4413", "Fournisseurs — retenues de garantie", 4, "credit", "detail", True, None),
    ("4415", "Fournisseurs — effets a payer", 4, "credit", "detail", True, None),
    ("4417", "Fournisseurs — factures non parvenues", 4, "credit", "detail", True, None),
    ("4418", "Autres fournisseurs et comptes rattaches", 4, "credit", "detail", True, None),
    ("4421", "Clients — avances et acomptes recus", 4, "credit", "detail", True, None),
    ("4425", "Clients — RRR a accorder, avoirs a etablir", 4, "credit", "detail", True, None),
    ("4431", "Remunerations dues au personnel", 4, "credit", "detail", False, None),
    ("4432", "Dettes pour conges a payer", 4, "credit", "detail", False, None),
    ("4437", "Charges du personnel a payer", 4, "credit", "detail", False, None),
    ("4438", "Organismes sociaux", 4, "credit", "detail", False, None),
    ("44381", "CNSS", 4, "credit", "detail", False, "4438"),
    ("44383", "Caisse de retraite (CIMR)", 4, "credit", "detail", False, "4438"),
    ("44384", "Mutuelle", 4, "credit", "detail", False, "4438"),
    ("44385", "AMO", 4, "credit", "detail", False, "4438"),
    ("4441", "Etat — impots, taxes et assimiles", 4, "credit", "detail", False, None),
    ("4443", "Etat — impots sur les resultats", 4, "credit", "detail", False, None),
    ("4445", "Etat — TVA facturee", 4, "credit", "detail", False, None),
    ("44551", "Etat — TVA due (ou credit de TVA)", 4, "credit", "detail", False, "4445"),
    ("4447", "Etat — impots et taxes a payer", 4, "credit", "detail", False, None),
    ("4448", "Etat — autres comptes crediteurs", 4, "credit", "detail", False, None),
    ("4450", "Comptes d'associes crediteurs", 4, "credit", "detail", True, None),
    ("4481", "Dettes sur acquisitions d'immobilisations", 4, "credit", "detail", True, None),
    ("4491", "Produits constates d'avance", 4, "credit", "detail", False, None),
    ("4493", "Interets courus et non echus a payer", 4, "credit", "detail", False, None),
    ("4497", "Comptes de repartition periodique des produits", 4, "credit", "detail", False, None),

    # ═══════ CLASSE 5 — Comptes de tresorerie ═══════
    ("5111", "Cheques a encaisser", 5, "debit", "detail", False, None),
    ("5112", "Effets a encaisser", 5, "debit", "detail", False, None),
    ("5113", "Virements de fonds", 5, "debit", "detail", False, None),
    ("5115", "Virements de fonds de tresorerie", 5, "debit", "detail", False, None),
    ("5141", "Banques (solde debiteur)", 5, "debit", "detail", True, None),
    ("5143", "Tresorerie generale", 5, "debit", "detail", False, None),
    ("5148", "Autres comptes de tresorerie", 5, "debit", "detail", False, None),
    ("5161", "Caisse", 5, "debit", "detail", False, None),
    ("5165", "Regies d'avances et accreditifs", 5, "debit", "detail", False, None),
    ("5520", "Credits d'escompte", 5, "credit", "detail", False, None),
    ("5530", "Credits de tresorerie", 5, "credit", "detail", False, None),
    ("5541", "Banques (solde crediteur)", 5, "credit", "detail", True, None),

    # ═══════ CLASSE 6 — Comptes de charges ═══════
    ("6111", "Achats de marchandises", 6, "debit", "detail", False, None),
    ("6114", "Variation des stocks de marchandises", 6, "debit", "detail", False, None),
    ("6121", "Achats de matieres premieres", 6, "debit", "detail", False, None),
    ("6122", "Achats de matieres et fournitures consommables", 6, "debit", "detail", False, None),
    ("6123", "Achats d'emballages", 6, "debit", "detail", False, None),
    ("6124", "Variation des stocks de matieres et fournitures", 6, "debit", "detail", False, None),
    ("6125", "Achats non stockes de matieres et fournitures", 6, "debit", "detail", False, None),
    ("6126", "Achats de travaux, etudes et prestations de services", 6, "debit", "detail", False, None),
    ("6128", "Achats de matieres et fournitures des exercices anterieurs", 6, "debit", "detail", False, None),
    ("6131", "Locations et charges locatives", 6, "debit", "detail", False, None),
    ("6132", "Redevances de credit-bail", 6, "debit", "detail", False, None),
    ("6133", "Entretien et reparations", 6, "debit", "detail", False, None),
    ("6134", "Primes d'assurances", 6, "debit", "detail", False, None),
    ("6135", "Remunerations du personnel exterieur", 6, "debit", "detail", False, None),
    ("6136", "Remunerations d'intermediaires et honoraires", 6, "debit", "detail", False, None),
    ("6137", "Redevances pour brevets, marques, licences", 6, "debit", "detail", False, None),
    ("6141", "Etudes, recherches et documentation", 6, "debit", "detail", False, None),
    ("6142", "Transports", 6, "debit", "detail", False, None),
    ("6143", "Deplacements, missions et receptions", 6, "debit", "detail", False, None),
    ("6144", "Publicite, publications et relations publiques", 6, "debit", "detail", False, None),
    ("6145", "Frais postaux et de telecommunications", 6, "debit", "detail", False, None),
    ("6146", "Cotisations et dons", 6, "debit", "detail", False, None),
    ("6147", "Services bancaires", 6, "debit", "detail", False, None),
    ("6148", "Autres charges externes des exercices anterieurs", 6, "debit", "detail", False, None),
    ("6149", "RRR obtenus sur autres charges externes", 6, "credit", "detail", False, None),
    ("6161", "Impots et taxes directes", 6, "debit", "detail", False, None),
    ("6165", "Impots et taxes indirectes", 6, "debit", "detail", False, None),
    ("6167", "Impots, taxes et droits assimiles", 6, "debit", "detail", False, None),
    ("6168", "Impots et taxes des exercices anterieurs", 6, "debit", "detail", False, None),
    ("6171", "Remunerations du personnel", 6, "debit", "detail", False, None),
    ("6174", "Charges sociales", 6, "debit", "detail", False, None),
    ("61741", "Cotisations de securite sociale (CNSS)", 6, "debit", "detail", False, "6174"),
    ("61742", "Cotisations aux caisses de retraite (CIMR)", 6, "debit", "detail", False, "6174"),
    ("61743", "Cotisations aux mutuelles", 6, "debit", "detail", False, "6174"),
    ("61744", "Prestations familiales", 6, "debit", "detail", False, "6174"),
    ("61745", "Assurance maladie obligatoire (AMO)", 6, "debit", "detail", False, "6174"),
    ("6176", "Charges sociales diverses", 6, "debit", "detail", False, None),
    ("6181", "Jetons de presence", 6, "debit", "detail", False, None),
    ("6182", "Pertes sur creances irrecouvrables", 6, "debit", "detail", False, None),
    ("6191", "DEA des immobilisations en non-valeurs", 6, "debit", "detail", False, None),
    ("6192", "DEA des immobilisations incorporelles", 6, "debit", "detail", False, None),
    ("6193", "DEA des immobilisations corporelles", 6, "debit", "detail", False, None),
    ("6194", "DEA des immobilisations financieres", 6, "debit", "detail", False, None),
    ("6196", "DEP de l'actif circulant", 6, "debit", "detail", False, None),
    ("6311", "Interets des emprunts et dettes", 6, "debit", "detail", False, None),
    ("6318", "Autres charges d'interets", 6, "debit", "detail", False, None),
    ("6331", "Pertes de change", 6, "debit", "detail", False, None),
    ("6386", "Escomptes accordes", 6, "debit", "detail", False, None),
    ("6393", "DEP des immobilisations financieres", 6, "debit", "detail", False, None),
    ("6396", "DEP des titres et valeurs de placement", 6, "debit", "detail", False, None),
    ("6511", "VNA des immobilisations incorporelles cedees", 6, "debit", "detail", False, None),
    ("6512", "VNA des immobilisations corporelles cedees", 6, "debit", "detail", False, None),
    ("6552", "Autres charges non courantes", 6, "debit", "detail", False, None),
    ("6581", "Penalites sur marches et debits", 6, "debit", "detail", False, None),
    ("6585", "Creances devenues irrecouvrables", 6, "debit", "detail", False, None),
    ("6594", "DEP non courantes des immobilisations", 6, "debit", "detail", False, None),
    ("6596", "DEP non courantes de l'actif circulant", 6, "debit", "detail", False, None),
    ("6701", "Impots sur les benefices", 6, "debit", "detail", False, None),

    # ═══════ CLASSE 7 — Comptes de produits ═══════
    ("7111", "Ventes de marchandises au Maroc", 7, "credit", "detail", False, None),
    ("7113", "Ventes de marchandises a l'etranger", 7, "credit", "detail", False, None),
    ("7118", "Ventes de marchandises des exercices anterieurs", 7, "credit", "detail", False, None),
    ("7119", "RRR accordes par l'entreprise", 7, "debit", "detail", False, None),
    ("7121", "Ventes de biens produits au Maroc", 7, "credit", "detail", False, None),
    ("7122", "Ventes de biens produits a l'etranger", 7, "credit", "detail", False, None),
    ("7124", "Ventes de services produits au Maroc", 7, "credit", "detail", False, None),
    ("7126", "Redevances pour brevets, marques, droits", 7, "credit", "detail", False, None),
    ("7128", "Ventes de biens et services des exercices anterieurs", 7, "credit", "detail", False, None),
    ("7129", "RRR accordes sur ventes de biens et services", 7, "debit", "detail", False, None),
    ("7131", "Variation des stocks de produits en cours", 7, "credit", "detail", False, None),
    ("7132", "Variation des stocks de biens produits", 7, "credit", "detail", False, None),
    ("7141", "Immobilisations produites par l'entreprise", 7, "credit", "detail", False, None),
    ("7161", "Subventions d'exploitation", 7, "credit", "detail", False, None),
    ("7181", "Produits divers de gestion courante", 7, "credit", "detail", False, None),
    ("7182", "Revenus des immeubles non affectes", 7, "credit", "detail", False, None),
    ("7191", "Reprises sur amortissements de l'immob.", 7, "credit", "detail", False, None),
    ("7196", "Reprises sur provisions de l'actif circulant", 7, "credit", "detail", False, None),
    ("7311", "Interets et produits assimiles", 7, "credit", "detail", False, None),
    ("7318", "Produits des autres immobilisations financieres", 7, "credit", "detail", False, None),
    ("7321", "Revenus des titres de participation", 7, "credit", "detail", False, None),
    ("7325", "Revenus des titres et valeurs de placement", 7, "credit", "detail", False, None),
    ("7331", "Gains de change", 7, "credit", "detail", False, None),
    ("7381", "Interets et autres produits financiers", 7, "credit", "detail", False, None),
    ("7386", "Escomptes obtenus", 7, "credit", "detail", False, None),
    ("7392", "Reprises sur provisions pour depreciation des immo. financieres", 7, "credit", "detail", False, None),
    ("7396", "Reprises sur provisions pour depreciation des TVP", 7, "credit", "detail", False, None),
    ("7511", "Produits de cession des immobilisations incorporelles", 7, "credit", "detail", False, None),
    ("7512", "Produits de cession des immobilisations corporelles", 7, "credit", "detail", False, None),
    ("7513", "Produits de cession des immobilisations financieres", 7, "credit", "detail", False, None),
    ("7561", "Subventions d'equilibre", 7, "credit", "detail", False, None),
    ("7581", "Penalites et debits percus", 7, "credit", "detail", False, None),
    ("7585", "Rentrees sur creances soldees", 7, "credit", "detail", False, None),
    ("7591", "Reprises non courantes sur amortissements", 7, "credit", "detail", False, None),
    ("7596", "Reprises non courantes sur provisions pour depreciation", 7, "credit", "detail", False, None),

    # ═══════ CLASSE 8 — Comptes de resultats ═══════
    ("8100", "Resultat d'exploitation", 8, "credit", "detail", False, None),
    ("8300", "Resultat financier", 8, "credit", "detail", False, None),
    ("8400", "Resultat courant", 8, "credit", "detail", False, None),
    ("8500", "Resultat non courant", 8, "credit", "detail", False, None),
    ("8600", "Resultat avant impots", 8, "credit", "detail", False, None),
    ("8800", "Resultat apres impots", 8, "credit", "detail", False, None),

    # ═══════ CLASSE 0/9 — Comptes hors bilan / analytiques ═══════
    ("9100", "Comptes analytiques de classe 1", 9, "debit", "detail", False, None),
    ("9200", "Comptes analytiques de classe 2", 9, "debit", "detail", False, None),
    ("9300", "Comptes analytiques de classe 3", 9, "debit", "detail", False, None),
    ("9810", "Engagements donnes", 9, "debit", "detail", False, None),
    ("9820", "Engagements recus", 9, "credit", "detail", False, None),
]

# ──────────────────────────────────────────────────────────────
# Journaux par defaut pour un dossier marocain
# Format: (code, label, journal_type)
# ──────────────────────────────────────────────────────────────

DEFAULT_JOURNALS: list[tuple[str, str, str]] = [
    ("AC", "Journal des achats", "achat"),
    ("VT", "Journal des ventes", "vente"),
    ("TR", "Journal de tresorerie", "tresorerie"),
    ("BQ", "Journal de banque", "tresorerie"),
    ("CS", "Journal de caisse", "tresorerie"),
    ("OD", "Journal des operations diverses", "od"),
    ("AN", "Journal des a-nouveaux", "an"),
    ("ST", "Journal de situation", "situation"),
]


async def seed_pcm_accounts(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> int:
    """Seed the standard PCM accounts for a dossier. Returns count of created accounts.
    Skips if accounts already exist for this dossier."""
    existing_count = (
        await db.execute(
            select(func.count(Account.id)).where(
                Account.tenant_id == tenant_id,
                Account.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    if existing_count > 0:
        return 0  # Already seeded — skip to avoid UniqueConstraint violation

    count = 0
    for number, label, acct_class, nature, acct_type, is_lettrable, parent in PCM_ACCOUNTS:
        account = Account(
            tenant_id=tenant_id,
            dossier_id=dossier_id,
            number=number,
            label=label,
            account_class=acct_class,
            nature=nature,
            account_type=acct_type,
            is_lettrable=is_lettrable,
            is_system=True,
            parent_number=parent,
        )
        db.add(account)
        count += 1
    await db.flush()
    return count


async def seed_default_journals(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> int:
    """Seed default journals for a dossier. Returns count of created journals.
    Skips if journals already exist for this dossier."""
    existing_count = (
        await db.execute(
            select(func.count(Journal.id)).where(
                Journal.tenant_id == tenant_id,
                Journal.dossier_id == dossier_id,
            )
        )
    ).scalar() or 0

    if existing_count > 0:
        return 0  # Already seeded — skip

    count = 0
    for code, label, journal_type in DEFAULT_JOURNALS:
        journal = Journal(
            tenant_id=tenant_id,
            dossier_id=dossier_id,
            code=code,
            label=label,
            journal_type=journal_type,
        )
        db.add(journal)
        count += 1
    await db.flush()
    return count


async def seed_dossier_defaults(
    db: AsyncSession, tenant_id: uuid.UUID, dossier_id: uuid.UUID
) -> dict:
    """Seed all default data for a new dossier (PCM + journals)."""
    accounts_count = await seed_pcm_accounts(db, tenant_id, dossier_id)
    journals_count = await seed_default_journals(db, tenant_id, dossier_id)
    return {
        "accounts_seeded": accounts_count,
        "journals_seeded": journals_count,
    }
