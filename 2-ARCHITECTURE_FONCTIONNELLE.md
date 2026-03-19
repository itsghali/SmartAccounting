# EASYACCOUNTING — Architecture Fonctionnelle Complète

## ERP SaaS marocain unifié — Document d'architecture fonctionnelle détaillée

**Version** : 1.0
**Date** : 18 mars 2026
**Statut** : Draft initial
**Référence** : PRD_EasyAccounting v1.0
**Classification** : Confidentiel — Usage interne

---

## Table des matières

1. [Socle Plateforme](#1-socle-plateforme)
2. [Comptabilité](#2-comptabilité)
3. [TVA et Fiscalité](#3-tva-et-fiscalité)
4. [Clôture / Réouverture / À-nouveaux](#4-clôture--réouverture--à-nouveaux)
5. [Paie & RH](#5-paie--rh)
6. [Gestion Commerciale](#6-gestion-commerciale)
7. [Immobilisations](#7-immobilisations)
8. [Analytique & Budgets](#8-analytique--budgets)
9. [Reporting & Pilotage](#9-reporting--pilotage)
10. [Gestion Documentaire](#10-gestion-documentaire)
11. [Notifications](#11-notifications)
12. [Audit & Traçabilité](#12-audit--traçabilité)
13. [IA Intégrée](#13-ia-intégrée)
14. [Moteur de Règles Métier](#14-moteur-de-règles-métier)

---

# 1. Socle Plateforme

## 1.1 Objectif métier

Fournir le socle transverse multi-tenant, multi-sociétés et multi-dossiers sur lequel reposent tous les modules fonctionnels. Ce socle garantit l'isolation des données, la gestion des identités, les droits d'accès granulaires, le paramétrage global et la capacité à servir simultanément des cabinets comptables (centaines de dossiers) et des PME mono-entité.

## 1.2 Sous-modules

| Code | Sous-module | Description |
|------|------------|-------------|
| SOC-TEN | Gestion des tenants | Création, suspension, suppression logique d'un espace locataire |
| SOC-ORG | Structure organisationnelle | Sociétés, établissements, dossiers au sein d'un tenant |
| SOC-IAM | Identité & Accès | Utilisateurs, rôles, permissions, MFA, sessions |
| SOC-PAR | Paramétrage global | Devises, langues, formats de date, fuseaux horaires |
| SOC-LIC | Licences & Abonnements | Plans tarifaires, quotas, modules activés |
| SOC-API | API Gateway | Routage, authentification, rate limiting, versioning |
| SOC-EVT | Bus d'événements | Publication/souscription d'événements inter-modules |
| SOC-MIG | Migration & Import | Outils d'import depuis Atlas, Sage, Excel |

## 1.3 Fonctionnalités détaillées

### 1.3.1 Gestion des tenants (SOC-TEN)

- **Provisioning automatique** : à la souscription, un tenant est créé avec son schéma PostgreSQL isolé, son espace de stockage S3, et ses paramètres par défaut.
- **Isolation des données** : chaque requête SQL est filtrée par `tenant_id` via Row-Level Security. Aucune fuite de données inter-tenant n'est possible.
- **Suspension** : un tenant en défaut de paiement est suspendu (accès lecture seule pendant 30 jours, puis gel total). Les données ne sont jamais supprimées avant 10 ans (obligation légale marocaine).
- **Contexte de tenant** : chaque requête HTTP porte le `tenant_id` dans le JWT. Le middleware injecte le contexte de tenant dans chaque service.

### 1.3.2 Structure organisationnelle (SOC-ORG)

- **Hiérarchie** : Tenant → Société(s) → Établissement(s) → Dossier(s).
- **Société** : entité juridique avec ICE, IF, RC, patente, CNSS employeur, forme juridique, capital, adresse, logo, cachet. Chaque société a ses propres paramètres comptables, fiscaux et sociaux.
- **Dossier** : unité de travail comptable. Pour un cabinet, un dossier = un client du cabinet. Pour une PME, un dossier = l'entreprise elle-même. Chaque dossier possède son plan de comptes, ses journaux, ses exercices.
- **Établissement** : site physique d'une société (siège, usine, agence). Pertinent pour la paie (CNSS par établissement).
- **Basculement rapide** : l'utilisateur peut changer de dossier/société en un clic sans rechargement de page (context switching).

### 1.3.3 Identité & Accès (SOC-IAM)

- **Utilisateurs** : email unique par tenant, nom, prénom, téléphone, statut (actif/inactif/suspendu).
- **Authentification** : email + mot de passe (bcrypt/argon2), MFA TOTP (obligatoire pour les admins), reset password par email, verrouillage après 5 tentatives échouées.
- **Sessions** : JWT access token (15 min) + refresh token (7 jours). Révocation immédiate possible.
- **Rôles prédéfinis** : Administrateur, Expert-comptable, Collaborateur comptable, Gestionnaire de paie, Commercial, Responsable stock, Lecture seule, Client (portail).
- **Permissions granulaires** : matrice Module × Action (lire, créer, modifier, supprimer, valider, exporter) × Périmètre (tous dossiers, dossiers assignés).
- **Droits par dossier** : un collaborateur ne voit que les dossiers qui lui sont affectés. L'affectation est gérée par l'administrateur ou l'expert-comptable.
- **SSO** (V3) : SAML 2.0 / OIDC pour les entreprises.

### 1.3.4 Paramétrage global (SOC-PAR)

- **Devise de référence** : MAD par défaut. Support multi-devises avec table de taux de change (saisie manuelle ou import automatique).
- **Format de date** : JJ/MM/AAAA par défaut (configurable).
- **Langue** : Français (défaut), Arabe, Anglais.
- **Fuseau horaire** : Africa/Casablanca (UTC+1).
- **Séparateurs numériques** : espace pour milliers, virgule pour décimales (convention marocaine/française).
- **Exercice par défaut** : 01/01 – 31/12 (modifiable par société).

### 1.3.5 Migration & Import (SOC-MIG)

- **Import AtlasCompta** : plan de comptes, journaux, écritures, à-nouveaux, immobilisations.
- **Import AtlasPaie** : salariés, rubriques, historique bulletins.
- **Import AtlasCom** : clients, produits, factures, stock.
- **Import Sage** : plan de comptes, écritures (format Sage export).
- **Import Excel générique** : modèle téléchargeable, validation stricte, rapport d'erreurs.
- **Processus** : upload → parsing → validation → preview → confirmation → import → rapport.

## 1.4 Objets métier principaux

| Objet | Attributs clés | Cardinalité |
|-------|---------------|-------------|
| `Tenant` | id, nom, plan, statut, date_creation, date_suspension | 1 par client souscripteur |
| `Société` | id, tenant_id, raison_sociale, forme_juridique, ICE, IF, RC, patente, cnss_employeur, capital, adresse, logo, cachet, modele_comptable (normal/simplifié) | N par tenant |
| `Établissement` | id, société_id, nom, adresse, cnss_etablissement | N par société |
| `Dossier` | id, société_id, nom, exercice_courant_id, plan_comptable_id, statut | N par société |
| `Utilisateur` | id, tenant_id, email, nom, prenom, role_id, mfa_active, statut | N par tenant |
| `Rôle` | id, tenant_id, nom, permissions[] | N par tenant |
| `Permission` | module, action, périmètre | Configurable par rôle |
| `AffectationDossier` | utilisateur_id, dossier_id | N-N |

## 1.5 Règles métier structurantes

| ID | Règle | Détail |
|----|-------|--------|
| SOC-R01 | Isolation totale | Aucune donnée d'un tenant ne peut être visible par un autre tenant. |
| SOC-R02 | Un dossier = un plan de comptes | Chaque dossier a son propre plan de comptes (copié depuis le CGNC à la création, puis personnalisable). |
| SOC-R03 | Pas de suppression physique | Tout objet est soft-deleted (champ `deleted_at`). Conservation minimale 10 ans. |
| SOC-R04 | Audit trail obligatoire | Chaque création, modification, suppression est tracée (voir domaine 12). |
| SOC-R05 | ICE obligatoire | Toute société doit avoir un ICE valide (15 chiffres). |
| SOC-R06 | Admin ≥ 1 | Un tenant doit toujours avoir au moins un utilisateur administrateur actif. |
| SOC-R07 | MFA admin | L'authentification MFA est obligatoire pour le rôle Administrateur. |

## 1.6 Workflows détaillés

### Workflow : Création d'un nouveau dossier

```
Administrateur/Expert-comptable
        │
        ▼
┌─────────────────────┐
│ 1. Sélection société │
└────────┬────────────┘
         ▼
┌─────────────────────────────┐
│ 2. Saisie infos dossier     │
│    - Nom du dossier          │
│    - Modèle comptable        │
│      (normal / simplifié)    │
│    - Date début 1er exercice │
│    - Date fin 1er exercice   │
└────────┬────────────────────┘
         ▼
┌─────────────────────────────┐
│ 3. Initialisation auto :     │
│    - Copie plan comptable    │
│      CGNC (normal/simplifié) │
│    - Création journaux       │
│      par défaut (AC,VT,BQ,   │
│      CA,OD,PA,AN)            │
│    - Création exercice N     │
│    - Création périodes        │
│      mensuelles               │
└────────┬────────────────────┘
         ▼
┌─────────────────────────────┐
│ 4. Affectation utilisateurs  │
│    - Collaborateurs assignés │
│    - Droits par module        │
└────────┬────────────────────┘
         ▼
┌─────────────────────────────┐
│ 5. Dossier prêt à l'emploi  │
│    Statut : ACTIF             │
└──────────────────────────────┘
```

### Workflow : Migration depuis Atlas

```
┌──────────┐    ┌───────────────┐    ┌────────────┐    ┌──────────┐
│ 1.Upload │───▶│ 2.Parsing &   │───▶│ 3.Preview  │───▶│ 4.Import │
│ fichiers │    │   Validation  │    │   & Mapping│    │  définit │
│ Atlas    │    │   (rapport    │    │   (corr.   │    │  + Log   │
│          │    │    erreurs)   │    │   comptes) │    │          │
└──────────┘    └───────────────┘    └────────────┘    └──────────┘
                       │                                     │
                       ▼                                     ▼
               ┌───────────────┐                    ┌──────────────┐
               │ Erreurs :     │                    │ Rapport de   │
               │ - Comptes     │                    │ migration :  │
               │   inexistants │                    │ - N écritures│
               │ - Déséquilibre│                    │ - N salariés │
               │ - Dates hors  │                    │ - N clients  │
               │   exercice    │                    │ - Anomalies  │
               └───────────────┘                    └──────────────┘
```

## 1.7 États / statuts métier

| Objet | Statuts possibles | Transitions |
|-------|------------------|-------------|
| Tenant | `actif`, `suspendu`, `gelé`, `résilié` | actif → suspendu → gelé → résilié (linéaire). suspendu → actif (réactivation). |
| Société | `active`, `inactive` | active ↔ inactive |
| Dossier | `actif`, `archivé` | actif → archivé. archivé → actif (réactivation). |
| Utilisateur | `actif`, `inactif`, `suspendu`, `verrouillé` | actif ↔ inactif. actif → verrouillé (5 tentatives). verrouillé → actif (déverrouillage admin). |

## 1.8 Écrans / interfaces principales

| Écran | Description | Rôle principal |
|-------|-------------|----------------|
| **Dashboard de tenant** | Vue d'ensemble : sociétés, dossiers, utilisateurs, abonnement | Administrateur |
| **Gestion des sociétés** | CRUD sociétés avec paramétrage complet | Administrateur |
| **Gestion des dossiers** | Liste des dossiers, création, archivage, basculement rapide | Administrateur, Expert-comptable |
| **Gestion des utilisateurs** | CRUD utilisateurs, affectation rôles et dossiers | Administrateur |
| **Gestion des rôles** | Matrice des permissions par rôle | Administrateur |
| **Sélecteur de dossier** | Widget global (header) permettant de changer de dossier | Tous |
| **Assistant de migration** | Wizard d'import depuis Atlas/Sage/Excel | Administrateur |
| **Paramétrage société** | Formulaire complet : identité juridique, fiscal, social | Administrateur |

## 1.9 Interactions avec les autres modules

| Module destination | Nature de l'interaction |
|-------------------|------------------------|
| Tous les modules | Le contexte `tenant_id`, `société_id`, `dossier_id` est injecté dans chaque requête. Tous les modules filtrent leurs données par ce contexte. |
| MOD-COMPTA | Le dossier fournit le plan de comptes, les journaux, l'exercice courant. |
| MOD-PAIE | La société fournit le CNSS employeur, les établissements. |
| MOD-AUDIT | Chaque action du socle est tracée dans l'audit trail. |
| MOD-NOTIF | Les événements de sécurité (connexion, MFA, verrouillage) déclenchent des notifications. |

## 1.10 Points de vigilance

- **Performance du context switching** : le changement de dossier doit être instantané (< 200ms). Ne pas recharger la page entière : seul le contexte de données change.
- **Isolation des schémas** : surveiller la prolifération de schémas PostgreSQL au-delà de 1 000 tenants. Envisager le sharding si nécessaire.
- **Migration Atlas** : les formats de fichiers Atlas ne sont pas documentés publiquement. Prévoir un reverse-engineering et des tests sur des fichiers réels.
- **RGPD / CNDP** : les données personnelles (salariés, utilisateurs) doivent être exportables et pseudonymisables sur demande (loi 09-08).

## 1.11 Obligatoire en MVP

- Multi-tenant avec isolation par schéma
- Multi-dossiers avec basculement rapide
- Gestion des utilisateurs, rôles et permissions
- Authentification email + MFA
- Paramétrage société (ICE, IF, RC, CNSS)
- Import Excel générique
- Import AtlasCompta (plan de comptes + écritures)

## 1.12 Ce qui peut venir après

- SSO SAML/OIDC (V3)
- Import AtlasPaie et AtlasCom (V2/V3)
- Import Sage (V2)
- API publique documentée pour intégrations tierces (V2)
- Multi-langue arabe (V3)
- Portail client (V4)

---

# 2. Comptabilité

## 2.1 Objectif métier

Fournir un module de comptabilité générale complet, conforme au Plan Comptable Marocain (CGNC), permettant la saisie, la validation, le lettrage, le rapprochement bancaire et l'édition de tous les états financiers réglementaires. Le module doit supporter le modèle normal et le modèle simplifié, gérer les journaux, exercices, périodes, et permettre l'industrialisation de la saisie pour les cabinets multi-dossiers.

## 2.2 Sous-modules

| Code | Sous-module | Description |
|------|------------|-------------|
| CPT-PCM | Plan comptable | Gestion du plan de comptes CGNC |
| CPT-JRN | Journaux | Paramétrage et gestion des journaux |
| CPT-EXR | Exercices & Périodes | Cycle de vie des exercices |
| CPT-ECR | Saisie comptable | Saisie, import, modèles, récurrence |
| CPT-LET | Lettrage | Lettrage manuel, auto, IA |
| CPT-RAP | Rapprochement bancaire | Import relevés, rapprochement |
| CPT-EDT | Éditions | Journal, grand livre, balance, bilan, CPC, ESG |
| CPT-LIA | Liasse fiscale | Génération liasse + EDI XML |

## 2.3 Fonctionnalités détaillées

### 2.3.1 Plan comptable (CPT-PCM)

**Plan CGNC pré-chargé** :
- À la création d'un dossier, le plan comptable CGNC est copié dans le dossier (modèle normal ou simplifié selon le choix).
- Classes 0 à 9 gérées.
- Structure hiérarchique : classe (1 chiffre) → rubrique (2 chiffres) → poste (3 chiffres) → compte (4 chiffres) → sous-compte (5+ chiffres).
- Comptes CGNC de base : non modifiables (code, intitulé protégés). L'utilisateur peut uniquement les activer/désactiver.
- Sous-comptes libres : l'utilisateur peut créer des subdivisions au-delà de 4 chiffres (ex : 61111001 = Achats matières premières fournisseur X).

**Attributs d'un compte** :

| Attribut | Description |
|----------|-------------|
| `code` | Numéro du compte (ex : 6111) |
| `intitulé` | Libellé du compte |
| `classe` | Classe CGNC (0-9) |
| `type` | Bilan / Gestion / Hors-bilan / Analytique / Résultat |
| `sens_habituel` | Débiteur / Créditeur |
| `collectif` | Oui/Non (comptes de tiers avec auxiliaires) |
| `tva_applicable` | Taux de TVA par défaut (si pertinent) |
| `imputation_analytique` | Obligatoire / Optionnelle / Interdite |
| `actif` | Oui/Non |
| `système` | Oui (CGNC, non modifiable) / Non (créé par l'utilisateur) |
| `date_création` | Date de création |
| `date_fermeture` | Date de désactivation |

**Comptes auxiliaires** :
- Les comptes collectifs (3411 Fournisseurs, 3421 Clients) sont gérés via des tiers.
- Chaque tiers (client/fournisseur) génère un compte auxiliaire automatique (ex : 3421-CLI001).
- Le grand livre auxiliaire donne le détail par tiers ; le compte collectif donne le solde agrégé.

### 2.3.2 Journaux (CPT-JRN)

**Journaux par défaut** (créés à l'initialisation du dossier) :

| Code | Type | Libellé | Contrepartie par défaut |
|------|------|---------|------------------------|
| AC | Achat | Journal des achats | 4411 (Fournisseurs) |
| VT | Vente | Journal des ventes | 3421 (Clients) |
| BQ01 | Banque | Banque principale | 5141 (Banque) |
| CA | Caisse | Caisse | 5161 (Caisse) |
| OD | OD | Opérations diverses | — |
| PA | Paie | Journal de paie | — |
| AN | AN | À-nouveaux | — |

**Règles des journaux** :
- Numérotation séquentielle par journal et par exercice. Format : `{CODE_JOURNAL}-{EXERCICE}-{SÉQUENCE}` (ex : AC-2026-000001).
- Pas de rupture dans la séquence : si une écriture est annulée, elle est extournée, pas supprimée.
- Un journal de banque par compte bancaire.
- Le journal AN est réservé aux écritures d'à-nouveaux (générées automatiquement).

### 2.3.3 Saisie comptable (CPT-ECR)

**Modes de saisie** :

| Mode | Description | Cible utilisateur |
|------|-------------|-------------------|
| Saisie au journal | Écran classique : sélection journal → saisie ligne par ligne (date, compte, libellé, débit, crédit) | Comptable expérimenté |
| Saisie rapide guidée | Assistants par type d'opération (facture achat, facture vente, règlement, OD) avec pré-remplissage des comptes | Collaborateur junior |
| Saisie par scan (IA) | Dépôt d'un document → OCR → suggestion d'écriture → validation | Tous |
| Import Excel | Upload d'un fichier selon modèle → validation → import | Migration, saisie en masse |
| Écritures récurrentes | Programmation d'écritures automatiques avec périodicité | Loyers, abonnements |
| Duplication | Copie d'une écriture existante avec modification | Écritures similaires |
| Modèles d'écriture | Application d'un modèle prédéfini avec montants ajustables | Opérations répétitives |

**Contrôles à la saisie** :

| Contrôle | Niveau | Description |
|----------|--------|-------------|
| Équilibre | Bloquant | Σ débits = Σ crédits, sinon impossible de sauvegarder |
| Compte existant | Bloquant | Le compte doit exister dans le plan et être actif |
| Compte non collectif | Bloquant | Interdiction de saisir directement sur un compte collectif (utiliser l'auxiliaire) |
| Date dans l'exercice | Bloquant | La date doit appartenir à l'exercice courant (ou un exercice ouvert) |
| Période non verrouillée | Bloquant | La période correspondant à la date ne doit pas être clôturée |
| Journal cohérent | Avertissement | Vérifier que le type d'opération correspond au journal (ex : pas de facture dans le journal de banque) |
| Doublon potentiel | Avertissement | L'IA détecte un potentiel doublon (même montant, même date, même tiers) |
| Montant suspect | Avertissement | L'IA signale un montant anormalement élevé pour ce type d'opération |

### 2.3.4 Cycle de vie d'une écriture comptable (FOCUS)

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  BROUILLARD│────▶│  VALIDÉE   │────▶│  LETTRÉE   │────▶│  CLÔTURÉE  │
│            │     │            │     │ (partiel/  │     │            │
│ Modifiable │     │ Immuable   │     │  total)    │     │ Immuable   │
│ Supprimable│     │ Extournable│     │ Délettrable│     │ Verrouillée│
└────────────┘     └──────┬─────┘     └────────────┘     └────────────┘
      │                   │
      │                   ▼
      │            ┌────────────┐
      │            │ EXTOURNÉE  │
      │            │            │
      │            │ Écriture   │
      │            │ inverse    │
      │            │ créée      │
      └────────────┘────────────┘
```

**États détaillés** :

| État | Description | Actions possibles | Transition vers |
|------|-------------|-------------------|-----------------|
| `BROUILLARD` | Écriture en cours de saisie. Pas encore officielle. | Modifier, Supprimer, Valider | → VALIDÉE |
| `VALIDÉE` | Écriture officielle. Le numéro de pièce est attribué définitivement. Apparaît dans les états. | Extourner, Lettrer | → LETTRÉE, → EXTOURNÉE |
| `LETTRÉE` | Écriture rapprochée avec une contrepartie (ex : facture ↔ règlement). | Délettrer | → VALIDÉE (si délettrée) |
| `EXTOURNÉE` | Écriture annulée par une écriture inverse. L'écriture originale reste visible mais marquée. | Aucune | Terminal (sauf si l'extourne elle-même est extournée) |
| `CLÔTURÉE` | Écriture appartenant à un exercice clôturé. | Aucune | Terminal |

**Anatomie d'une écriture comptable** :

```
Écriture (JournalEntry)
├── id                    UUID
├── dossier_id            Référence dossier
├── journal_id            Référence journal
├── numero_piece          Séquentiel par journal (ex: AC-2026-000042)
├── date_ecriture         Date comptable
├── date_saisie           Horodatage de création
├── libelle_general       Libellé de l'écriture
├── reference_externe     Numéro de facture, référence pièce
├── statut                BROUILLARD | VALIDÉE | EXTOURNÉE | CLÔTURÉE
├── origine               MANUELLE | IMPORT | IA | AUTO_PAIE | AUTO_COM | AUTO_TVA | AUTO_IMMO | AUTO_AN
├── ecriture_source_id    Référence si extourne ou auto-générée
├── validee_par           Utilisateur ayant validé
├── validee_le            Date de validation
├── pieces_jointes[]      Documents attachés (GED)
├── tags_analytiques[]    Ventilation analytique
│
└── Lignes (JournalEntryLine[])
    ├── id                UUID
    ├── compte_id         Référence au plan comptable
    ├── tiers_id          Référence au tiers (si compte collectif)
    ├── libelle_ligne     Libellé spécifique à la ligne
    ├── debit             Montant débit (0 si crédit)
    ├── credit            Montant crédit (0 si débit)
    ├── devise            Code devise (MAD par défaut)
    ├── montant_devise    Montant en devise étrangère
    ├── taux_change       Taux de conversion
    ├── code_tva          Référence au taux de TVA
    ├── montant_tva       Montant de TVA calculé
    ├── lettre            Code de lettrage (ex: AA, AB...)
    ├── date_echeance     Date d'échéance (pour les tiers)
    ├── ventilation_analytique[]  Répartition sur les axes
    └── reconciliation_id  Référence au rapprochement bancaire
```

### 2.3.5 Lettrage (CPT-LET)

**Principe** : le lettrage consiste à rapprocher des lignes d'écriture sur un même compte de tiers (la facture et le règlement) pour identifier les créances/dettes soldées.

**Modes de lettrage** :

| Mode | Mécanisme | Quand |
|------|-----------|-------|
| Manuel | L'utilisateur sélectionne les lignes à lettrer sur un compte auxiliaire. Le système vérifie que la somme des débits = somme des crédits pour le groupe sélectionné. | Par défaut |
| Automatique | Le système rapproche par : montant exact, référence pièce, ou combinaison montant + date. | En masse (fin de mois) |
| IA assisté | L'IA propose des groupes de lettrage basés sur des patterns historiques (correspondance fournisseur, montant approchant avec tolérance configurable). | Suggestion permanente |
| Partiel | Si le règlement ne couvre qu'une partie de la facture, le lettrage partiel est possible. Le solde restant est marqué comme non lettré. | Règlements partiels |

**Code de lettrage** : lettres séquentielles par compte (AA, AB, AC… ZZ, AAA…).

**Délettrage** : action réversible qui supprime le code de lettrage des lignes concernées. Tracé dans l'audit trail.

### 2.3.6 Rapprochement bancaire (CPT-RAP)

**Processus** :

```
┌───────────────┐    ┌────────────────┐    ┌─────────────────┐
│ 1. Import     │───▶│ 2. Parsing     │───▶│ 3. Rapprochement│
│    relevé     │    │    + Affichage  │    │    auto + manuel│
│    bancaire   │    │    lignes       │    │                 │
│ (CSV/OFX/MT940)    │    importées    │    │ Écritures compta│
└───────────────┘    └────────────────┘    │ vs Lignes relevé│
                                           └────────┬────────┘
                                                    ▼
                                           ┌─────────────────┐
                                           │ 4. État de       │
                                           │    rapprochement │
                                           │ Solde comptable  │
                                           │ ± Suspens        │
                                           │ = Solde banque   │
                                           └─────────────────┘
```

**Formats supportés** :

| Format | Description | Priorité |
|--------|-------------|----------|
| CSV | Format générique configurable (mapping des colonnes) | P0 |
| OFX | Open Financial Exchange | P0 |
| MT940 | SWIFT standard (utilisé par les banques marocaines) | P0 |
| CAMT.053 | ISO 20022 | P1 |

**Règles de rapprochement automatique** :
1. Correspondance exacte : montant identique + date identique (±2 jours).
2. Correspondance par référence : référence pièce dans le libellé du relevé.
3. Correspondance par montant : montant identique, date dans un intervalle configurable.
4. IA : apprentissage des patterns récurrents (ex : virement mensuel du même émetteur).

## 2.4 Objets métier principaux

| Objet | Description |
|-------|-------------|
| `PlanComptable` | Collection de comptes pour un dossier donné |
| `Compte` | Entrée du plan comptable avec ses attributs |
| `Journal` | Journal comptable avec type et séquence |
| `Exercice` | Période fiscale avec dates début/fin et statut |
| `Période` | Subdivision mensuelle de l'exercice |
| `ÉcritureComptable` | En-tête d'écriture (pièce) |
| `LigneÉcriture` | Ligne de débit ou crédit |
| `ModèleÉcriture` | Template réutilisable |
| `ÉcritureRécurrente` | Programmation d'écriture automatique |
| `Lettrage` | Groupe de lignes lettrées |
| `RelevéBancaire` | Relevé importé avec ses lignes |
| `LigneRelevé` | Ligne du relevé bancaire |
| `Rapprochement` | Lien entre ligne de relevé et ligne d'écriture |

## 2.5 Règles métier structurantes

| ID | Règle |
|----|-------|
| CPT-R01 | Toute écriture validée doit être équilibrée : Σ débits = Σ crédits. |
| CPT-R02 | La numérotation des pièces est séquentielle par journal et par exercice, sans rupture. |
| CPT-R03 | Une écriture validée ne peut pas être modifiée. Seule l'extourne est possible. |
| CPT-R04 | Une écriture ne peut porter que sur un exercice ouvert et une période non verrouillée. |
| CPT-R05 | Les comptes collectifs (3411, 3421) ne peuvent pas recevoir de saisie directe. Seuls les auxiliaires sont mouvementés. |
| CPT-R06 | Le plan comptable CGNC de base ne peut pas être supprimé ni modifié (code, intitulé, classe). |
| CPT-R07 | Le lettrage n'est possible que sur les comptes de tiers et les comptes de banque. |
| CPT-R08 | Le rapprochement bancaire lie une ligne de relevé à une ou plusieurs lignes d'écriture. Le solde de rapprochement doit converger vers zéro. |
| CPT-R09 | Les écritures d'origine automatique (paie, commercial, TVA, immobilisations, à-nouveaux) portent une référence à leur source et ne sont pas modifiables directement. |
| CPT-R10 | Chaque écriture doit avoir au minimum 2 lignes (un débit et un crédit). |

## 2.6 Éditions et reporting comptable

| État | Description | Format | Filtres |
|------|-------------|--------|---------|
| **Journal** | Liste des écritures par journal | PDF, Excel | Période, journal, statut |
| **Grand livre** | Mouvements et soldes par compte | PDF, Excel | Période, compte (de…à), tiers, lettré/non lettré |
| **Grand livre auxiliaire** | Détail par tiers pour les comptes collectifs | PDF, Excel | Tiers, période |
| **Balance générale** | Soldes débiteurs/créditeurs par compte | PDF, Excel | Période, classe, N/N-1 |
| **Balance auxiliaire** | Soldes par tiers | PDF, Excel | Type de tiers, période |
| **Balance âgée** | Créances/dettes par tranche d'ancienneté | PDF, Excel | Date de référence, tranches (30/60/90/120j) |
| **Bilan** | Actif / Passif conforme CGNC | PDF, Excel | Exercice, modèle (normal/simplifié) |
| **CPC** | Compte de Produits et Charges | PDF, Excel | Exercice, modèle |
| **ESG** | État des Soldes de Gestion | PDF, Excel | Exercice |
| **Tableau de financement** | Emplois et ressources | PDF, Excel | Exercice |
| **État de rapprochement** | Rapprochement bancaire | PDF, Excel | Compte banque, date |

## 2.7 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Plan comptable** | Arborescence navigable du plan, recherche, ajout de sous-comptes, activation/désactivation |
| **Liste des journaux** | Configuration des journaux, séquences, comptes de contrepartie |
| **Saisie au journal** | Grille de saisie avec auto-complétion sur les comptes, calcul automatique de l'équilibre |
| **Saisie rapide** | Formulaire guidé par type d'opération (facture, règlement, OD) |
| **Saisie par scan** | Zone de drop + preview OCR + formulaire d'écriture pré-rempli |
| **Import Excel** | Upload + preview + validation + rapport d'erreurs |
| **Lettrage** | Écran split : lignes non lettrées à gauche, proposition de lettrage à droite |
| **Rapprochement bancaire** | Écran split : relevé bancaire à gauche, écritures compta à droite, drag-and-drop |
| **Grand livre** | Liste des mouvements avec filtres, drill-down vers l'écriture source |
| **Balance** | Tableau des soldes avec comparaison N/N-1, export |
| **Bilan / CPC** | Présentation conforme CGNC avec drill-down vers les comptes |
| **Modèles d'écriture** | CRUD des modèles avec preview |

## 2.8 Interactions avec les autres modules

| Module source | Flux vers Comptabilité | Événement déclencheur |
|--------------|----------------------|----------------------|
| MOD-PAIE | Écritures de paie (charges personnel, cotisations, net à payer) | `paie.période.validée` |
| MOD-COM | Écritures de vente (client, produit, TVA) | `facture_vente.émise` |
| MOD-COM | Écritures d'achat (fournisseur, charge, TVA) | `facture_achat.validée` |
| MOD-COM | Écritures de règlement (banque/caisse, tiers) | `règlement.enregistré` |
| MOD-COM | Écritures de variation de stock | `inventaire.validé` |
| MOD-IMMO | Dotations aux amortissements | `dotation.calculée` |
| MOD-IMMO | Écritures de cession | `immobilisation.cédée` |
| MOD-TVA | Écriture de liquidation TVA | `déclaration_tva.validée` |
| MOD-COMPTA → MOD-TVA | Écritures avec TVA alimentent le calcul TVA | `écriture.validée` (si TVA) |
| MOD-COMPTA → MOD-ANA | Ventilation analytique des écritures | `écriture.validée` (si analytique) |
| MOD-COMPTA → MOD-REPORT | Données de soldes et mouvements | Lecture directe |

## 2.9 Points de vigilance

- **Performance des états financiers** : le bilan et le CPC nécessitent l'agrégation de toutes les écritures de l'exercice. Pour un dossier de 100 000 écritures, indexer les tables par (dossier_id, exercice_id, compte_id, date).
- **Numérotation sans rupture** : en cas de suppression d'un brouillard, le numéro ne doit pas être réattribué (les brouillards n'ont pas de numéro de pièce officiel — le numéro est attribué à la validation).
- **Écritures auto-générées** : les écritures provenant de la paie, du commercial ou des immobilisations ne doivent pas pouvoir être modifiées manuellement. Seule l'extourne est possible, et elle doit générer un avertissement ("cette écriture provient du module X — l'extourner peut créer une incohérence inter-modules").
- **Multi-devises** : les écritures en devise étrangère doivent être converties en MAD au taux du jour. Les écarts de conversion sont gérés dans les comptes CGNC appropriés (classe 6/7).

## 2.10 Obligatoire en MVP

- Plan comptable CGNC (normal + simplifié)
- Journaux (AC, VT, BQ, CA, OD, AN)
- Saisie au journal et saisie rapide
- Contrôle d'équilibre
- Validation / brouillard / extourne
- Modèles d'écriture et duplication
- Import Excel
- Lettrage manuel et automatique
- Rapprochement bancaire (CSV + OFX)
- Journal, Grand livre, Balance, Bilan, CPC, ESG
- Liasse fiscale + EDI XML
- Export PDF / Excel
- Pièces jointes

## 2.11 Ce qui peut venir après

- Saisie par scan avec IA (V2)
- Lettrage IA (V2)
- Rapprochement IA (V2)
- Écritures récurrentes (V2)
- Saisie par lot (V2)
- Multi-devises avec conversion automatique (V2)
- Tableau de financement (V2)
- Rapprochement MT940 / CAMT.053 (V2)
- Personnalisation des états (V3)

---

# 3. TVA et Fiscalité

## 3.1 Objectif métier

Automatiser le calcul, le contrôle et la déclaration de la TVA selon les régimes marocains. Assister à la production de la liasse fiscale et des fichiers EDI XML. Fournir les outils de contrôle de cohérence entre la comptabilité et les déclarations fiscales.

## 3.2 Sous-modules

| Code | Sous-module |
|------|------------|
| TVA-PAR | Paramétrage TVA |
| TVA-CAL | Calcul TVA périodique |
| TVA-DEC | Déclaration TVA |
| TVA-LIQ | Liquidation comptable |
| TVA-CTR | Contrôle de cohérence |
| FIS-LIA | Liasse fiscale |
| FIS-EDI | EDI XML DGI |
| FIS-IS | Assistance IS/IR professionnel |
| FIS-RAS | Retenue à la source |

## 3.3 Fonctionnalités détaillées

### 3.3.1 Paramétrage TVA (TVA-PAR)

**Régimes** :

| Régime | Description | Impact sur le calcul |
|--------|-------------|---------------------|
| Encaissement | TVA exigible à l'encaissement (prestation de services) | La TVA collectée est comptabilisée à la date du règlement |
| Débit | TVA exigible à la facturation (vente de biens) | La TVA collectée est comptabilisée à la date de la facture |
| Exonéré avec droit de déduction | Exportations, zones franches | TVA déductible récupérable, pas de TVA collectée |
| Exonéré sans droit de déduction | Éducation, santé | Pas de TVA collectée, pas de TVA déductible |

**Taux configurables** (via moteur de règles) :

| Code | Taux | Application par défaut |
|------|------|----------------------|
| TVA20 | 20% | Biens et services courants |
| TVA14 | 14% | Transport, énergie |
| TVA10 | 10% | Hôtellerie, restauration, professions libérales |
| TVA07 | 7% | Eau, pharmacie, fournitures scolaires |
| TVA00 | 0% | Exportations |
| EXON | — | Opérations exonérées |

**Prorata de déduction** :
- Pour les entreprises réalisant à la fois des opérations taxables et exonérées sans droit de déduction.
- Prorata = (CA taxable + CA exonéré avec droit de déduction) / CA total.
- Le prorata est calculé annuellement et appliqué à la TVA déductible.
- Régularisation en fin d'année si le prorata définitif diffère du prorata provisionnel.

### 3.3.2 Cycle déclaratif TVA (FOCUS)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CYCLE DÉCLARATIF TVA                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. COLLECTE DES DONNÉES                                        │
│     ├── Écritures validées de la période                        │
│     ├── Comptes de TVA mouvementés (4455x, 3455x)              │
│     ├── Régime par opération (encaissement/débit)               │
│     └── Crédit de TVA de la période précédente                  │
│                                                                  │
│  2. CALCUL AUTOMATIQUE                                          │
│     ├── TVA collectée (par taux)                                │
│     │   └── 4455x : 20%, 14%, 10%, 7%                          │
│     ├── TVA déductible sur charges                              │
│     │   └── 34551 (avec décalage d'un mois)                    │
│     ├── TVA déductible sur immobilisations                      │
│     │   └── 34552 (pas de décalage)                             │
│     ├── Crédit de TVA reporté (période N-1)                     │
│     └── Solde = Collectée - Déductible - Crédit reporté         │
│         ├── Si > 0 : TVA due (à payer à l'État)                │
│         └── Si < 0 : Crédit de TVA (reporté sur N+1)           │
│                                                                  │
│  3. CONTRÔLE DE COHÉRENCE (IA + Règles)                         │
│     ├── CA déclaré vs CA comptabilisé                           │
│     ├── TVA collectée vs écritures de vente                     │
│     ├── TVA déductible vs factures d'achat                      │
│     ├── Vérification prorata (si applicable)                    │
│     ├── Détection anomalies : TVA sans contrepartie             │
│     └── Signalement des écarts                                  │
│                                                                  │
│  4. VALIDATION PAR L'UTILISATEUR                                │
│     └── Confirmation manuelle obligatoire                       │
│                                                                  │
│  5. GÉNÉRATION                                                   │
│     ├── Formulaire de déclaration (PDF)                         │
│     ├── Fichier EDI XML (si applicable)                         │
│     └── Écriture de liquidation TVA en comptabilité             │
│         ├── Débit 4455x (TVA collectée)                         │
│         ├── Crédit 34551/34552 (TVA déductible)                 │
│         └── Crédit/Débit 4456 (TVA due/Crédit TVA)             │
│                                                                  │
│  6. ARCHIVAGE                                                    │
│     └── Déclaration archivée avec toutes les pièces             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3.3 Règle du décalage d'un mois

La TVA déductible sur charges n'est récupérable qu'au titre du mois suivant celui de la facturation.

**Exemple** : une facture fournisseur datée du 15 janvier → la TVA déductible correspondante apparaît dans la déclaration de février.

**Exception** : la TVA sur immobilisations est déductible immédiatement (pas de décalage).

**Implémentation** : chaque ligne d'écriture avec TVA déductible porte une `date_deductibilité` = `date_facture + 1 mois`. Le calcul TVA filtre par `date_deductibilité` ∈ période déclarée.

### 3.3.4 Liasse fiscale (FIS-LIA)

**Tableaux de la liasse** :

| Tableau | Intitulé | Source |
|---------|----------|--------|
| Bilan - Actif | Actif immobilisé + Actif circulant + Trésorerie | Soldes comptes classes 2, 3, 5 |
| Bilan - Passif | Financement permanent + Passif circulant + Trésorerie passif | Soldes comptes classes 1, 4, 5 |
| CPC | Compte de Produits et Charges | Soldes comptes classes 6, 7 |
| ESG | État des Soldes de Gestion | Calcul à partir du CPC |
| TF | Tableau de Financement | Variation des postes du bilan |
| A1 | État de répartition du capital social | Paramétrage manuel |
| B1 | Tableau des immobilisations | MOD-IMMO |
| B2 | Tableau des amortissements | MOD-IMMO |
| B3 | Tableau des plus/moins-values de cession | MOD-IMMO |
| C1 | Provisions | Comptes 15xx, 19xx, 29xx, 39xx |
| D | Tableau des créances | Comptes 34xx avec ventilation par échéance |
| E | Tableau des dettes | Comptes 44xx avec ventilation par échéance |
| F | Passage du résultat net comptable au résultat net fiscal | Réintégrations + Déductions |
| G | Détail de la TPPRF et des produits de participation | Comptes spécifiques |
| H | Détermination du résultat courant après impôt | Calcul IS |
| I | Affectation du résultat | Décision AG |
| J | Informations complémentaires | Effectifs, rémunérations, etc. |

### 3.3.5 EDI XML DGI (FIS-EDI)

- Format XML conforme aux spécifications de la DGI (Direction Générale des Impôts).
- Le fichier contient l'ensemble des tableaux de la liasse fiscale.
- Validé par un XSD fourni par la DGI.
- Le fichier est généré, téléchargé par l'utilisateur, et déposé manuellement sur le portail de la DGI (pas de dépôt automatique en V1).

## 3.4 Objets métier principaux

| Objet | Attributs clés |
|-------|---------------|
| `DéclarationTVA` | id, dossier_id, période, type (mensuelle/trimestrielle), tva_collectée, tva_déductible_charges, tva_déductible_immo, crédit_reporté, solde, statut, validée_par, validée_le |
| `LigneDéclarationTVA` | id, déclaration_id, taux_tva, base_ht, montant_tva, type (collectée/déductible) |
| `CréditTVA` | id, dossier_id, période_origine, montant_initial, montant_consommé, montant_restant |
| `LiasseFiscale` | id, dossier_id, exercice_id, statut, tableaux[], fichier_xml, générée_par, générée_le |
| `TableauLiasse` | id, liasse_id, code_tableau, lignes[] |

## 3.5 Règles métier structurantes

| ID | Règle |
|----|-------|
| TVA-R01 | La déclaration TVA est mensuelle si CA > 1M MAD, trimestrielle sinon. |
| TVA-R02 | Le décalage d'un mois s'applique à la TVA déductible sur charges (pas sur immobilisations). |
| TVA-R03 | Le crédit de TVA se reporte de période en période jusqu'à épuisement. |
| TVA-R04 | La liquidation TVA génère une écriture automatique en comptabilité. |
| TVA-R05 | Le prorata est recalculé annuellement. La régularisation est comptabilisée en fin d'exercice. |
| TVA-R06 | L'utilisateur doit valider explicitement chaque déclaration (l'IA ne peut pas valider). |
| TVA-R07 | La liasse fiscale doit être conforme au modèle (normal ou simplifié) du dossier. |
| TVA-R08 | Le fichier EDI XML doit être valide selon le XSD de la DGI. |

## 3.6 États / statuts métier

| Objet | Statuts |
|-------|---------|
| DéclarationTVA | `brouillon` → `calculée` → `validée` → `déposée` |
| LiasseFiscale | `en_cours` → `générée` → `validée` → `déposée` |

## 3.7 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Paramétrage TVA** | Configuration des taux, régime, prorata, seuils |
| **Déclaration TVA** | Tableau de calcul avec drill-down, anomalies, validation |
| **Historique TVA** | Liste des déclarations passées avec réédition |
| **Liasse fiscale** | Navigation par tableau, prévisualisation, génération PDF/XML |
| **Contrôle de cohérence** | Dashboard des écarts TVA/compta |

## 3.8 Interactions avec les autres modules

| Module | Interaction |
|--------|------------|
| MOD-COMPTA | Lecture des écritures avec TVA pour calcul. Écriture de liquidation TVA. |
| MOD-IMMO | TVA déductible sur immobilisations (sans décalage). Tableau B1/B2 de la liasse. |
| MOD-COM | CA par taux de TVA (ventes). TVA sur achats. |
| MOD-REPORT | Indicateurs TVA dans les dashboards. |
| Moteur de règles | Taux TVA, seuils de régime, prorata. |

## 3.9 Points de vigilance

- **Décalage d'un mois** : la logique est subtile et source fréquente de bugs. Tester exhaustivement avec des cas limites (facture du 31 janvier, facture à cheval sur deux périodes).
- **Changement de régime** : si une entreprise passe de trimestriel à mensuel en cours d'année, les périodes de transition doivent être gérées.
- **XSD DGI** : le format peut changer chaque année. Mettre en place une veille et un processus de mise à jour rapide.

## 3.10 Obligatoire en MVP

- Paramétrage TVA (taux, régimes)
- Calcul TVA automatique (collectée, déductible, crédit)
- Décalage d'un mois
- Déclaration mensuelle et trimestrielle
- Écriture de liquidation
- Contrôle de cohérence basique
- Liasse fiscale complète (modèle normal + simplifié)
- EDI XML
- Export PDF

## 3.11 Ce qui peut venir après

- Prorata de déduction (V2)
- Contrôle de cohérence IA avancé (V2)
- Assistance IS/IR professionnel (V3)
- Retenue à la source (V3)
- Dépôt automatique EDI (V4)

---

# 4. Clôture / Réouverture / À-nouveaux

## 4.1 Objectif métier

Gérer le cycle de vie complet d'un exercice comptable : ouverture, travaux courants, pré-clôture, clôture définitive, génération des à-nouveaux, et réouverture exceptionnelle. Ce processus est critique car il engage la responsabilité juridique du professionnel comptable.

## 4.2 Sous-modules

| Code | Sous-module |
|------|------------|
| CLO-PER | Gestion des périodes |
| CLO-PRE | Pré-clôture et contrôles |
| CLO-DEF | Clôture définitive |
| CLO-ANV | Génération des à-nouveaux |
| CLO-REO | Réouverture exceptionnelle |

## 4.3 Cycle d'exercice comptable (FOCUS)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CYCLE DE VIE D'UN EXERCICE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐                                                           │
│  │ CRÉÉ     │  L'exercice est défini (dates début/fin, périodes)        │
│  └────┬─────┘                                                           │
│       ▼                                                                  │
│  ┌──────────┐                                                           │
│  │ OUVERT   │  Saisie comptable autorisée. Travaux courants.           │
│  │          │  Les périodes sont ouvertes une par une.                  │
│  └────┬─────┘                                                           │
│       │  ┌─────────────────────────────────────────────┐                │
│       │  │ CYCLE PÉRIODIQUE (mensuel)                    │               │
│       │  │                                               │               │
│       │  │  Période M ouverte                            │               │
│       │  │     │                                         │               │
│       │  │     ▼                                         │               │
│       │  │  Saisie des écritures de M                    │               │
│       │  │     │                                         │               │
│       │  │     ▼                                         │               │
│       │  │  Travaux de fin de mois :                     │               │
│       │  │  - Rapprochement bancaire                     │               │
│       │  │  - Lettrage                                   │               │
│       │  │  - Déclaration TVA                            │               │
│       │  │  - Dotations aux amortissements               │               │
│       │  │     │                                         │               │
│       │  │     ▼                                         │               │
│       │  │  Verrouillage période M                       │               │
│       │  │  (aucune écriture ne peut plus être ajoutée)  │               │
│       │  │     │                                         │               │
│       │  │     ▼                                         │               │
│       │  │  Ouverture période M+1                        │               │
│       │  └───────────────────────────────────────────────┘               │
│       │                                                                  │
│       ▼                                                                  │
│  ┌──────────────┐                                                       │
│  │ PRÉ-CLÔTURE  │  Assistant de clôture lancé.                          │
│  │              │  Contrôles automatiques exécutés.                     │
│  │              │  Anomalies signalées.                                 │
│  │              │  Corrections effectuées.                              │
│  └────┬─────────┘                                                       │
│       ▼                                                                  │
│  ┌──────────────┐                                                       │
│  │ CLÔTURÉ      │  Exercice verrouillé définitivement.                  │
│  │              │  À-nouveaux N+1 générés.                              │
│  │              │  Aucune modification possible.                        │
│  └────┬─────────┘                                                       │
│       │                                                                  │
│       ▼  (cas exceptionnel, admin uniquement)                           │
│  ┌──────────────┐                                                       │
│  │ RÉOUVERT     │  Exercice temporairement déverrouillé.               │
│  │              │  Modifications tracées.                               │
│  │              │  Re-clôture obligatoire.                              │
│  │              │  À-nouveaux N+1 recalculés.                           │
│  └──────────────┘                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.4 Contrôles de pré-clôture

| # | Contrôle | Niveau | Description |
|---|----------|--------|-------------|
| 1 | Équilibre des journaux | Bloquant | Σ débits = Σ crédits pour chaque journal |
| 2 | Écritures en brouillard | Bloquant | Aucune écriture ne doit rester en brouillard |
| 3 | Rapprochement bancaire | Avertissement | Le rapprochement bancaire de chaque compte doit être réalisé |
| 4 | Lettrage des tiers | Avertissement | Vérifier que les comptes de tiers sont lettrés (signaler les soldes non lettrés) |
| 5 | TVA soldée | Avertissement | Toutes les déclarations TVA de l'exercice doivent être validées |
| 6 | Amortissements constatés | Bloquant | Les dotations aux amortissements de l'exercice doivent être comptabilisées |
| 7 | Provisions | Avertissement | Vérifier que les provisions habituelles sont constatées |
| 8 | Charges/produits régularisés | Avertissement | Vérifier les CCA, PCA, FAR, FNP |
| 9 | Résultat cohérent | Avertissement | Le résultat net doit être cohérent (pas d'anomalie évidente) |
| 10 | Liasse fiscale générée | Information | La liasse peut être générée avant ou après la clôture |

## 4.5 Génération des à-nouveaux

**Règles de calcul** :

| Type de compte | Traitement |
|---------------|-----------|
| Comptes de bilan (classes 1-5) | Report du solde débiteur ou créditeur |
| Comptes de gestion (classes 6-7) | Soldés (non reportés). Le résultat est viré au compte 1191 ou 1199. |
| Comptes de tiers lettrés | Seules les lignes non lettrées sont reportées (reprise des lettres ouvertes) |
| Comptes hors bilan (classe 0) | Report du solde |
| Comptes analytiques (classe 9) | Non reportés (remis à zéro) |

**Écritures générées** :
- Journal : AN (À-Nouveaux)
- Date : 01/01/N+1 (premier jour du nouvel exercice)
- Une écriture d'à-nouveaux par compte avec solde non nul
- Pour les comptes de tiers : une ligne par lettre ouverte (détail du non lettré)

**À-nouveaux provisoires** :
- Générés en cours d'exercice pour les situations intermédiaires.
- Recalculés à chaque demande (pas de verrouillage).
- Marqués comme "provisoires" et non officiels.

## 4.6 Réouverture exceptionnelle

**Processus** :
1. Seul un administrateur peut initier une réouverture.
2. Motif obligatoire (champ texte).
3. Confirmation par saisie du mot de passe + MFA.
4. L'exercice passe en statut `RÉOUVERT`.
5. Les modifications sont possibles mais chaque action est tracée avec le motif de réouverture.
6. Les à-nouveaux de l'exercice N+1 sont invalidés et marqués "à recalculer".
7. À la fin des corrections, l'administrateur relance la clôture.
8. Les à-nouveaux N+1 sont recalculés.
9. Si l'exercice N+1 avait lui-même des écritures, un contrôle de cohérence est exécuté.

## 4.7 Objets métier

| Objet | Attributs clés |
|-------|---------------|
| `Exercice` | id, dossier_id, date_début, date_fin, statut, clôturé_par, clôturé_le, réouvert_par, réouvert_le, motif_réouverture |
| `Période` | id, exercice_id, mois, date_début, date_fin, verrouillée, verrouillée_par, verrouillée_le |
| `ContrôlePréClôture` | id, exercice_id, type_contrôle, résultat (OK/KO/WARNING), détail, date_exécution |
| `ÀNouveaux` | id, exercice_source_id, exercice_cible_id, type (définitif/provisoire), écritures_générées[], date_génération |

## 4.8 Règles métier structurantes

| ID | Règle |
|----|-------|
| CLO-R01 | La clôture est irréversible sauf réouverture exceptionnelle par un administrateur. |
| CLO-R02 | La clôture ne peut être effectuée que si tous les contrôles bloquants sont OK. |
| CLO-R03 | Les à-nouveaux sont générés automatiquement à la clôture. |
| CLO-R04 | Le verrouillage d'une période empêche toute saisie ou modification d'écriture dans cette période. |
| CLO-R05 | La réouverture invalide les à-nouveaux de l'exercice suivant. |
| CLO-R06 | Seul un utilisateur avec le rôle Administrateur ou Expert-comptable peut clôturer un exercice. |
| CLO-R07 | Un exercice ne peut être clôturé que si l'exercice précédent est clôturé (sauf premier exercice). |

## 4.9 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Gestion des exercices** | Liste des exercices, statuts, actions (créer, clôturer, réouvrir) |
| **Gestion des périodes** | Liste des mois de l'exercice, statuts, verrouillage/déverrouillage |
| **Assistant de clôture** | Wizard en étapes : contrôles → corrections → génération états → confirmation → clôture |
| **Rapport de pré-clôture** | Résultats des contrôles avec drill-down vers les anomalies |
| **Réouverture** | Formulaire avec motif obligatoire + double confirmation |

## 4.10 Interactions avec les autres modules

| Module | Interaction |
|--------|------------|
| MOD-COMPTA | Verrouillage des écritures à la clôture. Génération des à-nouveaux dans le journal AN. |
| MOD-TVA | Contrôle pré-clôture : toutes les déclarations TVA validées. |
| MOD-IMMO | Contrôle pré-clôture : amortissements constatés. Tableau des immobilisations pour la liasse. |
| MOD-PAIE | Contrôle pré-clôture : écritures de paie intégrées pour tous les mois. |
| MOD-AUDIT | Traçabilité complète de la clôture et de la réouverture. |

## 4.11 Obligatoire en MVP

- Gestion des exercices (création, ouverture, clôture)
- Gestion des périodes avec verrouillage
- Contrôles de pré-clôture (bloquants + avertissements)
- Clôture définitive avec verrouillage
- Génération des à-nouveaux définitifs
- Réouverture exceptionnelle avec traçabilité

## 4.12 Ce qui peut venir après

- À-nouveaux provisoires (V2)
- Assistant de clôture avec IA (suggestions de régularisation) (V2)
- Clôture en masse multi-dossiers (V3) — pour les cabinets

---

# 5. Paie & RH

## 5.1 Objectif métier

Fournir un module de paie marocaine complet gérant le cycle de vie du salarié, le calcul de la paie selon les règles marocaines (IR, CNSS, AMO, CIMR), la génération des bulletins, les déclarations sociales (DAMANCOM) et fiscales (état 9421), et l'intégration automatique des écritures comptables de paie. Le module doit supporter les conventions collectives, les rubriques personnalisées et les simulations brut ↔ net.

## 5.2 Sous-modules

| Code | Sous-module |
|------|------------|
| PAI-SAL | Gestion des salariés |
| PAI-RUB | Rubriques de paie |
| PAI-CAL | Moteur de calcul |
| PAI-BUL | Bulletins de paie |
| PAI-CON | Congés & Absences |
| PAI-PRT | Prêts salariés |
| PAI-DEC | Déclarations sociales & fiscales |
| PAI-INT | Intégration comptable |
| PAI-SIM | Simulateur brut ↔ net |

## 5.3 Fonctionnalités détaillées

### 5.3.1 Gestion des salariés (PAI-SAL)

**Fiche salarié — Données structurées** :

| Bloc | Champs |
|------|--------|
| Identité | Nom, prénom, CIN, date de naissance, lieu de naissance, nationalité, sexe, photo |
| Contact | Adresse, téléphone, email |
| Situation familiale | Marié/célibataire/divorcé/veuf, nombre de personnes à charge (max 6 pour IR), conjoint à charge |
| Contrat | Type (CDI/CDD/intérim/stage/ANAPEC), date d'embauche, date de fin (CDD), période d'essai, motif de départ |
| Poste | Intitulé du poste, catégorie professionnelle (cadre/employé/ouvrier), échelon, coefficient, convention collective |
| Rémunération | Salaire de base, mode de paiement (mensuel/quinzaine/hebdo), devise, RIB |
| Affiliations | N° CNSS salarié, N° CIMR, organisme mutuelle + N° adhérent, caisse de retraite complémentaire |
| Établissement | Rattachement à un établissement (si multi-établissements) |
| Historique | Historique des modifications de salaire, de poste, de catégorie (avec dates d'effet) |

**Statuts du salarié** :

```
EMBAUCHÉ ──▶ ACTIF ──▶ SUSPENDU ──▶ ACTIF
                │                      │
                ├──▶ EN_PRÉAVIS ──▶ SORTI
                │
                └──▶ SORTI (départ immédiat)
```

| Statut | Description |
|--------|-------------|
| `EMBAUCHÉ` | Fiche créée, pas encore en activité |
| `ACTIF` | Salarié en poste, inclus dans la paie |
| `SUSPENDU` | Congé sans solde, maladie longue durée — exclu de la paie |
| `EN_PRÉAVIS` | Préavis en cours, toujours dans la paie |
| `SORTI` | Départ effectif (démission, licenciement, fin CDD, retraite, décès) — exclu de la paie |

### 5.3.2 Rubriques de paie (PAI-RUB)

**Structure d'une rubrique** :

| Attribut | Description |
|----------|-------------|
| `code` | Code unique (ex : R001, R002...) |
| `intitulé` | Libellé affiché sur le bulletin |
| `type` | Gain / Retenue / Cotisation / Exonération |
| `nature` | Base / Prime / Indemnité / HS / Cotisation salariale / Cotisation patronale / IR |
| `formule` | Expression de calcul (ex : `salaire_base * taux_anciennete`) |
| `assiette` | Base sur laquelle le calcul s'applique |
| `taux` | Taux applicable (si applicable) |
| `plafond` | Plafond de calcul (si applicable) |
| `imposable` | Oui / Non / Partiellement |
| `cotisable_cnss` | Oui / Non |
| `soumise_ir` | Oui / Non |
| `ordre_calcul` | Ordre d'exécution dans la chaîne de paie |
| `système` | Oui (standard marocain, non modifiable) / Non (personnalisée) |
| `conditions` | Conditions d'application (ex : si ancienneté > 2 ans) |

**Rubriques prédéfinies** :

| Code | Intitulé | Formule |
|------|----------|---------|
| R-BASE | Salaire de base | `salaire_base` (mensuel) ou `salaire_base / jours_ouvrables * jours_travaillés` |
| R-ANC | Prime d'ancienneté | `salaire_base * taux_ancienneté` (5% après 2 ans, 10% après 5 ans, 15% après 12 ans, 20% après 20 ans, 25% après 25 ans) |
| R-HS25 | Heures sup 25% | `(salaire_base / 191) * nb_heures * 1.25` |
| R-HS50 | Heures sup 50% | `(salaire_base / 191) * nb_heures * 1.50` |
| R-HS100 | Heures sup 100% | `(salaire_base / 191) * nb_heures * 2.00` |
| R-CNSS-SAL | CNSS part salariale | `min(brut_cotisable, plafond_cnss) * taux_cnss_salarial + brut_cotisable * taux_amo_salarial` |
| R-CNSS-PAT | CNSS part patronale | Calcul analogue avec taux patronaux |
| R-CIMR-SAL | CIMR part salariale | `brut_cotisable * taux_cimr_salarial` |
| R-CIMR-PAT | CIMR part patronale | `brut_cotisable * taux_cimr_patronal` |
| R-MUT-SAL | Mutuelle salariale | `brut_cotisable * taux_mutuelle_salarial` |
| R-IR | IR mensuel | Calcul par le barème progressif (voir moteur de calcul) |
| R-ABS | Retenue absence | `salaire_base / jours_ouvrables * jours_absence` |
| R-PRET | Retenue prêt | Montant fixe (échéance du mois) |

### 5.3.3 Cycle de paie (FOCUS)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CYCLE DE PAIE MENSUELLE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1 — PRÉPARATION (J-5 à J-3 avant fin de mois)                   │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 1.1 Vérification des fiches salariés                 │               │
│  │     - Nouveaux embauchés saisis ?                    │               │
│  │     - Départs enregistrés ?                          │               │
│  │     - Modifications de salaire effectives ?          │               │
│  │                                                       │               │
│  │ 1.2 Saisie des éléments variables                    │               │
│  │     - Heures supplémentaires                         │               │
│  │     - Primes exceptionnelles                         │               │
│  │     - Absences non encore saisies                    │               │
│  │     - Avances et acomptes                            │               │
│  │                                                       │               │
│  │ 1.3 Vérification des congés et absences              │               │
│  │     - Congés validés impactant la paie               │               │
│  │     - Arrêts maladie avec justificatifs              │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  PHASE 2 — CALCUL (J-2)                                                │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 2.1 Calcul en masse pour tous les salariés actifs    │               │
│  │                                                       │               │
│  │ 2.2 Pour chaque salarié, le moteur exécute :         │               │
│  │     a) Calcul du BRUT                                │               │
│  │        = Base + Primes + HS + Indemnités             │
│  │        + Avantages en nature                         │               │
│  │                                                       │               │
│  │     b) Calcul du BRUT IMPOSABLE                      │               │
│  │        = Brut - Éléments exonérés d'IR               │               │
│  │                                                       │               │
│  │     c) Calcul du SALAIRE NET IMPOSABLE (SNI)         │               │
│  │        = Brut imposable                              │               │
│  │        - Frais professionnels (20%, plafond 2500/m)  │               │
│  │        - CNSS part salariale                         │               │
│  │        - CIMR part salariale                         │               │
│  │        - Mutuelle salariale                          │               │
│  │                                                       │               │
│  │     d) Calcul de l'IR MENSUEL                        │               │
│  │        = Application barème progressif au SNI mensuel│               │
│  │        - Déductions pour personnes à charge          │               │
│  │          (30 MAD/personne/mois, max 6)               │               │
│  │                                                       │               │
│  │     e) Calcul du NET À PAYER                         │               │
│  │        = Brut                                        │               │
│  │        - Cotisations salariales (CNSS+CIMR+Mut)      │               │
│  │        - IR                                          │               │
│  │        - Retenues (prêts, avances, absences)         │               │
│  │        + Indemnités non imposables                   │               │
│  │                                                       │               │
│  │     f) Calcul des cotisations patronales             │               │
│  │        - CNSS patronale                              │               │
│  │        - CIMR patronale                              │               │
│  │        - Mutuelle patronale                          │               │
│  │        - Allocations familiales                      │               │
│  │        - Taxe formation professionnelle              │               │
│  │                                                       │               │
│  │ 2.3 Contrôles automatiques                           │               │
│  │     - SMIG respecté ?                                │               │
│  │     - Plafond CNSS appliqué ?                        │               │
│  │     - Barème IR à jour ?                             │               │
│  │     - Net à payer positif ?                          │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  PHASE 3 — VÉRIFICATION (J-1)                                          │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 3.1 Récapitulatif de paie (tableau synthétique)      │               │
│  │     - Total brut, total cotisations, total IR,       │               │
│  │       total net à payer                              │               │
│  │     - Comparaison M vs M-1 (écarts significatifs)    │               │
│  │                                                       │               │
│  │ 3.2 Vérification individuelle (si anomalie)          │               │
│  │     - Drill-down sur le bulletin d'un salarié        │               │
│  │     - Simulation "what-if" (ajuster un élément)      │               │
│  │                                                       │               │
│  │ 3.3 Corrections éventuelles                          │               │
│  │     - Retour en Phase 1 si nécessaire                │               │
│  │     - Recalcul après correction                      │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  PHASE 4 — VALIDATION (J)                                               │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 4.1 Validation définitive par le responsable          │               │
│  │     ⚠ ACTION IRRÉVERSIBLE pour la période            │               │
│  │     - Les bulletins sont verrouillés                  │               │
│  │     - La période de paie passe en statut VALIDÉE      │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  PHASE 5 — SORTIES (J à J+2)                                           │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 5.1 Génération des bulletins de paie (PDF)            │               │
│  │ 5.2 Envoi par email aux salariés (optionnel)          │               │
│  │ 5.3 Génération fichier DAMANCOM (CNSS)                │               │
│  │ 5.4 Génération bordereau CNSS (Atlas BDS)             │               │
│  │ 5.5 Alimentation état 9421 (cumul annuel)             │               │
│  │ 5.6 Génération des écritures comptables de paie       │               │
│  │     → Journal PA                                      │               │
│  │     → Débit : 617x (charges personnel)                │               │
│  │     → Débit : 616x (cotisations patronales)           │               │
│  │     → Crédit : 4432 (rémunérations dues)              │               │
│  │     → Crédit : 4441-4447 (organismes sociaux)         │               │
│  │     → Crédit : 44525 (État – IR)                      │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  PHASE 6 — RÉGULARISATION ANNUELLE (décembre)                           │
│  ┌─────────────────────────────────────────────────────┐                │
│  │ 6.1 Recalcul IR annuel :                              │               │
│  │     IR_annuel = barème(SNI_cumulé_annuel)             │               │
│  │     - déductions personnes à charge × 12              │               │
│  │                                                       │               │
│  │ 6.2 Comparaison avec le cumul IR mensuel              │               │
│  │     Δ = IR_annuel - Σ(IR_mensuels_jan_à_nov)         │               │
│  │     Si Δ > 0 : complément IR sur bulletin décembre    │               │
│  │     Si Δ < 0 : remboursement sur bulletin décembre    │               │
│  │                                                       │               │
│  │ 6.3 Génération état 9421 définitif                    │               │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3.4 Simulateur brut ↔ net (PAI-SIM)

**Brut → Net** : saisie du salaire brut → calcul des cotisations et IR → affichage du net.

**Net → Brut** (calcul inverse) :
- Algorithme itératif : le système part du net cible, estime un brut, calcule le net correspondant, ajuste par dichotomie jusqu'à convergence (tolérance 0,01 MAD).
- Prend en compte : situation familiale, personnes à charge, taux CIMR, mutuelle.

### 5.3.5 Déclarations sociales (PAI-DEC)

**DAMANCOM** :
- Fichier TXT ou XML au format CNSS.
- Contenu : pour chaque salarié, N° CNSS, nom, prénom, salaire brut, jours travaillés, jours de congé.
- Fréquence : mensuelle.
- Le fichier est généré et téléchargé par l'utilisateur pour dépôt sur le portail CNSS.

**État 9421** :
- Déclaration annuelle des traitements et salaires.
- Pour chaque salarié : identité, salaire brut annuel, retenues, IR annuel.
- Généré automatiquement à partir des bulletins de paie de l'année.
- Export PDF + XML.

**Bordereau CNSS (Atlas BDS)** :
- Récapitulatif mensuel des cotisations CNSS par entreprise.
- Détail par salarié et total.

## 5.4 Objets métier principaux

| Objet | Description |
|-------|-------------|
| `Salarié` | Fiche complète du salarié |
| `Contrat` | Détails contractuels (type, dates, poste, rémunération) |
| `RubriquePaie` | Définition d'une rubrique de calcul |
| `PériodePaie` | Mois de paie avec statut |
| `BulletinPaie` | Résultat du calcul pour un salarié et une période |
| `LigneBulletin` | Détail d'une rubrique sur le bulletin |
| `Congé` | Demande de congé avec type, dates, statut |
| `Absence` | Enregistrement d'absence avec impact paie |
| `Prêt` | Prêt salarié avec échéancier |
| `ÉchéancePrêt` | Ligne de remboursement mensuel |
| `DéclarationDAMANCOM` | Fichier CNSS généré |
| `État9421` | Déclaration annuelle des salaires |

## 5.5 Règles métier structurantes

| ID | Règle |
|----|-------|
| PAI-R01 | Le SMIG doit être respecté : le salaire mensuel pour 191h ne peut être inférieur au SMIG en vigueur. |
| PAI-R02 | Le plafond CNSS (6 000 MAD/mois) s'applique aux cotisations long terme. L'AMO est sans plafond. |
| PAI-R03 | Les frais professionnels sont déduits à 20% du brut imposable, plafonnés à 2 500 MAD/mois (30 000 MAD/an). |
| PAI-R04 | Les personnes à charge ouvrent droit à une déduction de 30 MAD/personne/mois, maximum 6 personnes. |
| PAI-R05 | La prime d'ancienneté est calculée selon le barème légal : 5% (2-5 ans), 10% (5-12 ans), 15% (12-20 ans), 20% (20-25 ans), 25% (>25 ans). |
| PAI-R06 | Les heures supplémentaires sont majorées de 25% (jour), 50% (nuit, 21h-6h), 100% (repos hebdomadaire/jour férié). |
| PAI-R07 | La régularisation annuelle IR est obligatoire en décembre. |
| PAI-R08 | Un bulletin validé ne peut pas être modifié. Seul un bulletin complémentaire ou correctif est possible. |
| PAI-R09 | L'intégration comptable génère une écriture unique centralisée ou détaillée par salarié selon le paramétrage. |
| PAI-R10 | Le congé annuel est de 1,5 jour ouvrable par mois de travail effectif, majoré de 1,5 jour par tranche de 5 ans d'ancienneté. |

## 5.6 États / statuts métier

| Objet | Statuts |
|-------|---------|
| PériodePaie | `ouverte` → `calculée` → `vérifiée` → `validée` |
| BulletinPaie | `brouillon` → `calculé` → `validé` → `envoyé` |
| Congé | `demandé` → `approuvé` / `refusé` → `pris` → `annulé` |
| Prêt | `actif` → `en_remboursement` → `soldé` |

## 5.7 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Liste des salariés** | Tableau filtrable avec recherche, statut, actions |
| **Fiche salarié** | Formulaire multi-onglets (identité, contrat, paie, historique, congés, prêts) |
| **Saisie éléments variables** | Grille de saisie par salarié pour le mois |
| **Calcul de masse** | Lancement du calcul, barre de progression, résultats |
| **Récapitulatif de paie** | Tableau synthétique avec totaux et écarts M/M-1 |
| **Bulletin individuel** | Prévisualisation du bulletin avec drill-down sur chaque rubrique |
| **Simulateur brut/net** | Calculatrice interactive avec paramètres ajustables |
| **Gestion des congés** | Calendrier + soldes + historique |
| **Gestion des prêts** | Liste des prêts, échéanciers, soldes |
| **Déclarations** | Génération DAMANCOM, état 9421, BDS |

## 5.8 Interactions avec les autres modules

| Module | Interaction |
|--------|------------|
| MOD-COMPTA | Génération des écritures de paie dans le journal PA |
| Moteur de règles | Barème IR, taux CNSS, plafonds, SMIG, taux d'ancienneté |
| MOD-GED | Bulletins de paie archivés, contrats, attestations |
| MOD-REPORT | Masse salariale, effectifs, coûts par département |
| MOD-NOTIF | Alertes : fin de CDD, fin de période d'essai, congés non pris |

## 5.9 Points de vigilance

- **Précision des calculs** : les montants doivent être calculés au centime près. Utiliser des types décimaux (pas de float) pour éviter les erreurs d'arrondi.
- **Barème IR** : le barème change périodiquement. Stocker dans le moteur de règles avec date d'effet.
- **Régularisation annuelle** : algorithme complexe, surtout en cas de changement de situation familiale en cours d'année.
- **DAMANCOM** : le format est imposé par la CNSS et peut évoluer. Prévoir un parseur configurable.

## 5.10 Obligatoire en MVP (V2)

- Fiches salariés complètes
- Rubriques standard marocaines
- Calcul brut, cotisations CNSS/AMO/CIMR, IR, net
- Heures supplémentaires
- Congés et absences
- Prêts salariés
- Bulletins de paie (PDF)
- DAMANCOM
- État 9421
- Intégration comptable
- Simulateur brut/net
- Régularisation annuelle IR

## 5.11 Ce qui peut venir après

- Rubriques personnalisées avec formules avancées (V3)
- Bulletin de paie électronique avec signature (V3)
- Multi-établissements (V3)
- Avantages en nature (V3)
- Provision congés payés automatique (V3)
- Envoi email des bulletins (V3)
- Portail salarié (V4)

---

# 6. Gestion Commerciale

## 6.1 Objectif métier

Fournir un module de gestion commerciale complet couvrant le cycle de vente (devis → commande → livraison → facturation → encaissement), le cycle d'achat (commande → réception → facture fournisseur → règlement), la gestion du stock (entrées, sorties, inventaire, valorisation) et l'intégration automatique vers la comptabilité. Le module reprend les fonctionnalités d'AtlasCom en les modernisant.

## 6.2 Sous-modules

| Code | Sous-module |
|------|------------|
| COM-REF | Référentiels (clients, fournisseurs, produits) |
| COM-VTE | Cycle de vente |
| COM-ACH | Cycle d'achat |
| COM-RGL | Règlements & Encaissements |
| COM-STK | Gestion du stock |
| COM-INT | Intégration comptable |

## 6.3 Cycle commercial complet (FOCUS)

### 6.3.1 Cycle de vente

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  DEVIS  │───▶│ COMMANDE │───▶│LIVRAISON │───▶│ FACTURE  │───▶│RÈGLEMENT │
│         │    │  CLIENT  │    │  (BL)    │    │  VENTE   │    │  CLIENT  │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                    │               │               │
                                    ▼               ▼               ▼
                              ┌──────────┐   ┌──────────┐   ┌──────────┐
                              │ SORTIE   │   │ ÉCRITURE │   │ ÉCRITURE │
                              │ STOCK    │   │ VENTE    │   │ ENCAISS. │
                              │          │   │ (compta) │   │ (compta) │
                              └──────────┘   └──────────┘   └──────────┘
```

**États du document de vente** :

| Document | Statuts | Transitions |
|----------|---------|-------------|
| Devis | `brouillon` → `envoyé` → `accepté` / `refusé` / `expiré` | accepté → conversion en commande |
| Commande client | `confirmée` → `en_préparation` → `livrée_partiellement` → `livrée` / `annulée` | livrée → conversion en BL |
| Bon de livraison | `créé` → `validé` | validé → conversion en facture. Impact stock. |
| Facture de vente | `brouillon` → `émise` → `payée_partiellement` → `payée` / `annulée` (avoir) | émise → écriture comptable auto |
| Avoir | `brouillon` → `émis` | émis → écriture comptable auto + retour stock |

### 6.3.2 Cycle d'achat

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ COMMANDE │───▶│RÉCEPTION │───▶│ FACTURE  │───▶│RÈGLEMENT │
│FOURNISS. │    │  (BR)    │    │  ACHAT   │    │FOURNISS. │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │               │               │
                     ▼               ▼               ▼
               ┌──────────┐   ┌──────────┐   ┌──────────┐
               │ ENTRÉE   │   │ ÉCRITURE │   │ ÉCRITURE │
               │ STOCK    │   │ ACHAT    │   │ PAIEMENT │
               │          │   │ (compta) │   │ (compta) │
               └──────────┘   └──────────┘   └──────────┘
```

### 6.3.3 Gestion du stock

**Mouvements de stock** :

| Type de mouvement | Déclencheur | Impact |
|-------------------|-------------|--------|
| Entrée par réception | Bon de réception validé | +Qté, MAJ CMUP |
| Entrée par régularisation | Inventaire (surplus) | +Qté, écriture de régularisation |
| Sortie par livraison | Bon de livraison validé | -Qté |
| Sortie par régularisation | Inventaire (manquant) | -Qté, écriture de régularisation |
| Transfert inter-dépôts | Ordre de transfert | -Qté dépôt A, +Qté dépôt B |

**Valorisation** :

| Méthode | Calcul |
|---------|--------|
| CMUP (Coût Moyen Unitaire Pondéré) | `(Valeur stock existant + Valeur nouvelle entrée) / (Qté existante + Qté entrée)` |
| FIFO | Les sorties sont valorisées au coût des entrées les plus anciennes |

**Inventaire physique** :
1. L'utilisateur lance un inventaire (date, dépôt, familles de produits).
2. Le système fige le stock théorique à la date d'inventaire.
3. L'utilisateur saisit les quantités physiques constatées.
4. Le système calcule les écarts (excédents/manquants).
5. L'utilisateur valide les régularisations.
6. Les mouvements de régularisation sont créés.
7. Les écritures comptables de variation de stock sont générées (6031x/3111x).

## 6.4 Objets métier principaux

| Objet | Attributs clés |
|-------|---------------|
| `Client` | id, code, raison_sociale, ICE, IF, RC, adresse, contacts, conditions_paiement, plafond_crédit |
| `Fournisseur` | id, code, raison_sociale, ICE, IF, RC, adresse, contacts, conditions_achat |
| `Produit` | id, référence, désignation, famille_id, unité, prix_achat, prix_vente_ht, taux_tva, code_barre, stock_min, compte_vente, compte_achat |
| `FamilleProduit` | id, code, intitulé, parent_id (hiérarchie) |
| `DocumentCommercial` | id, type, numéro, date, tiers_id, lignes[], montant_ht, montant_tva, montant_ttc, statut |
| `LigneDocument` | id, document_id, produit_id, désignation, quantité, prix_unitaire_ht, remise_%, taux_tva, montant_ht, montant_tva |
| `Règlement` | id, type (encaissement/paiement), tiers_id, montant, date, mode_règlement, référence, factures_affectées[] |
| `MouvementStock` | id, produit_id, dépôt_id, type, quantité, valeur_unitaire, document_source, date |
| `Dépôt` | id, code, nom, adresse |
| `Inventaire` | id, dépôt_id, date, statut, lignes[] |

## 6.5 Règles métier structurantes

| ID | Règle |
|----|-------|
| COM-R01 | Chaque facture doit porter l'ICE du client (obligatoire par la loi marocaine). |
| COM-R02 | La numérotation des factures est séquentielle et sans rupture. |
| COM-R03 | Un avoir ne peut être émis que contre une facture existante. |
| COM-R04 | Le stock ne peut pas devenir négatif (sauf paramétrage explicite). |
| COM-R05 | La TVA est détaillée par taux sur chaque document commercial. |
| COM-R06 | L'intégration comptable est automatique et immédiate à l'émission de la facture. |
| COM-R07 | Le CMUP est recalculé à chaque entrée de stock. |
| COM-R08 | Un encaissement ne peut pas excéder le solde dû par le client. |

## 6.6 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Liste clients** | Tableau avec recherche, filtre, solde créances |
| **Fiche client** | Infos + historique documents + balance client |
| **Catalogue produits** | Grille avec familles, recherche, scan code-barres |
| **Saisie devis/commande/BL/facture** | Formulaire unifié avec lignes de produits, remises, TVA, totaux |
| **Suivi des commandes** | Tableau de bord des commandes avec progression |
| **Encaissements** | Saisie + affectation aux factures |
| **État du stock** | Stock par produit, par dépôt, valorisation |
| **Inventaire** | Saisie d'inventaire + calcul écarts + régularisation |
| **Échéancier client** | Créances par date d'échéance |

## 6.7 Interactions avec les autres modules

| Module | Interaction |
|--------|------------|
| MOD-COMPTA | Écritures de vente, achat, règlement, variation stock |
| MOD-TVA | CA par taux pour le calcul TVA |
| MOD-GED | Factures PDF archivées |
| MOD-REPORT | CA, marges, top clients/produits |
| MOD-IA | Suggestion de prix, détection anomalies |
| MOD-NOTIF | Alertes stock min, échéances, retards de paiement |

## 6.8 Intégration comptable

| Événement | Écriture générée |
|-----------|-----------------|
| Facture de vente émise | Débit 3421 (Client) / Crédit 711x (Ventes) / Crédit 4455x (TVA collectée) |
| Facture d'achat validée | Débit 611x (Achats) / Débit 3455x (TVA déductible) / Crédit 4411 (Fournisseur) |
| Encaissement client | Débit 514x (Banque) / Crédit 3421 (Client) |
| Paiement fournisseur | Débit 4411 (Fournisseur) / Crédit 514x (Banque) |
| Régularisation stock (manquant) | Débit 6031 (Variation stock) / Crédit 3111 (Stock) |
| Régularisation stock (excédent) | Débit 3111 (Stock) / Crédit 6031 (Variation stock) |

## 6.9 Obligatoire en MVP (V3)

- Clients, fournisseurs, produits, familles
- Devis, commandes client, BL, factures, avoirs
- Encaissements et paiements
- Stock (entrées, sorties, inventaire, CMUP)
- Intégration comptable automatique
- Export PDF, impression
- Codes-barres, recherche avancée

## 6.10 Ce qui peut venir après

- Cycle d'achat complet (BC fournisseur, BR) (V3+)
- Multi-dépôts et transferts (V3+)
- Grilles de prix par client/quantité (V4)
- Scan code-barres mobile (V4)
- Impression Bluetooth/WiFi (V4)
- Relance client automatique (V4)
- FIFO (V4)

---

# 7. Immobilisations

## 7.1 Objectif métier

Gérer le patrimoine immobilisé de l'entreprise : acquisition, amortissement (linéaire et dégressif selon les règles CGNC), cession, mise au rebut. Générer les écritures comptables de dotation et les tableaux réglementaires pour la liasse fiscale.

## 7.2 Sous-modules

| Code | Sous-module |
|------|------------|
| IMO-FIC | Fiches immobilisations |
| IMO-AMO | Calcul des amortissements |
| IMO-CES | Cessions et sorties |
| IMO-TAB | Tableaux réglementaires |
| IMO-INT | Intégration comptable |

## 7.3 Cycle des immobilisations (FOCUS)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ ACQUISITION  │───▶│ EN SERVICE   │───▶│ AMORTISSEMENT│
│              │    │              │    │ (périodique) │
│ Achat ou     │    │ Date de mise │    │ Dotation     │
│ production   │    │ en service   │    │ mensuelle/   │
│              │    │              │    │ annuelle     │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                    ┌──────────┼──────────┐
                                    ▼          ▼          ▼
                              ┌──────────┐┌──────────┐┌──────────┐
                              │ CESSION  ││MISE AU   ││TOTALEMENT│
                              │          ││REBUT     ││AMORTIE   │
                              │Plus/moins││VNC → 0   ││VNC = 0   │
                              │value     ││Perte     ││En service│
                              └──────────┘└──────────┘└──────────┘
```

## 7.4 Fonctionnalités détaillées

### 7.4.1 Fiche immobilisation

| Champ | Description |
|-------|-------------|
| Code | Identifiant unique auto-généré |
| Désignation | Description de l'immobilisation |
| Catégorie | Selon nomenclature CGNC (terrain, construction, matériel, mobilier, véhicule, immobilisation incorporelle, etc.) |
| Date d'acquisition | Date d'achat ou de production |
| Date de mise en service | Date de début d'amortissement (peut être ≠ date acquisition) |
| Valeur d'origine | Montant d'achat HT (ou coût de production) |
| TVA récupérée | Montant de TVA déductible sur immobilisation |
| Durée de vie | En années, selon la catégorie CGNC |
| Méthode d'amortissement | Linéaire / Dégressif / Exceptionnel |
| Taux d'amortissement | Calculé (linéaire = 100/durée) ou paramétré (dégressif) |
| Valeur résiduelle | Valeur estimée en fin de vie (généralement 0 au Maroc) |
| Fournisseur | Référence fournisseur |
| N° facture | Référence de la facture d'acquisition |
| Localisation | Site, bureau, département |
| N° inventaire | Numéro physique de l'inventaire des immobilisations |
| Compte d'immobilisation | Compte CGNC (classe 2) |
| Compte d'amortissement | Compte CGNC (classe 28) |
| Compte de dotation | Compte CGNC (classe 619) |

### 7.4.2 Calcul des amortissements

**Amortissement linéaire** :
- Dotation annuelle = Valeur d'origine / Durée de vie
- Prorata temporis la première et dernière année (en jours ou en mois selon le paramétrage)
- La première année : dotation × (nombre de jours restants / 360) depuis la date de mise en service

**Amortissement dégressif** :
- Taux dégressif = Taux linéaire × Coefficient
- Coefficients fiscaux marocains : 1.5 (durée 3-4 ans), 2 (durée 5-6 ans), 3 (durée > 6 ans)
- Comparaison annuelle : si dotation linéaire restante > dotation dégressive, on passe au linéaire pour les années restantes

**Plan d'amortissement** : tableau prévisionnel année par année :

| Année | VNC début | Dotation | Amortissement cumulé | VNC fin |
|-------|-----------|----------|---------------------|---------|
| 2026 | 100 000 | 20 000 | 20 000 | 80 000 |
| 2027 | 80 000 | 20 000 | 40 000 | 60 000 |
| ... | ... | ... | ... | ... |

### 7.4.3 Cession d'immobilisation

**Calcul** :
- VNC à la date de cession = Valeur d'origine - Amortissements cumulés à la date de cession
- Plus-value = Prix de cession - VNC (si > 0)
- Moins-value = VNC - Prix de cession (si > 0)

**Écritures de cession** :
1. Dotation complémentaire (du 01/01 à la date de cession)
2. Sortie de l'immobilisation :
   - Débit 28xx (Amort. cumulés) + Débit 651x (VNC des immo cédées) → Crédit 2xxx (Immobilisation)
3. Produit de cession :
   - Débit 514x (Banque) ou 3481 (Créance) → Crédit 751x (Produit de cession)

## 7.5 Objets métier principaux

| Objet | Description |
|-------|-------------|
| `Immobilisation` | Fiche complète de l'immobilisation |
| `CatégorieImmobilisation` | Catégorie CGNC avec durée et méthode par défaut |
| `PlanAmortissement` | Tableau prévisionnel |
| `LignePlanAmortissement` | Détail annuel (dotation, VNC) |
| `Dotation` | Dotation constatée pour une période |
| `Cession` | Enregistrement de cession avec calcul plus/moins-value |

## 7.6 Règles métier structurantes

| ID | Règle |
|----|-------|
| IMO-R01 | Le plan d'amortissement est recalculé automatiquement si la durée ou la méthode change. |
| IMO-R02 | La TVA sur immobilisation est déductible immédiatement (pas de décalage d'un mois). |
| IMO-R03 | Le prorata temporis s'applique la première année (à partir de la date de mise en service). |
| IMO-R04 | Une immobilisation totalement amortie (VNC = 0) reste dans le registre tant qu'elle est en service. |
| IMO-R05 | Les dotations génèrent automatiquement des écritures dans le journal OD. |
| IMO-R06 | Le tableau des immobilisations (B1/B2) est alimenté automatiquement pour la liasse fiscale. |

## 7.7 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Registre des immobilisations** | Liste filtrable par catégorie, statut, localisation |
| **Fiche immobilisation** | Formulaire complet + plan d'amortissement |
| **Calcul des dotations** | Lancement du calcul pour une période, preview, validation |
| **Cession** | Assistant de cession avec calcul automatique |
| **Tableau des immobilisations** | État conforme liasse fiscale (B1/B2/B3) |

## 7.8 Obligatoire en MVP

- Fiches immobilisations
- Catégories CGNC
- Amortissement linéaire + dégressif
- Plan d'amortissement
- Dotation automatique avec écritures comptables
- Cession et mise au rebut
- Tableaux B1/B2/B3 liasse fiscale
- Import Excel

## 7.9 Ce qui peut venir après

- Amortissement exceptionnel (V2)
- Réévaluation (V3)
- Inventaire physique des immobilisations (V3)
- Gestion des composants (V4)

---

# 8. Analytique & Budgets

## 8.1 Objectif métier

Permettre l'analyse des charges et produits selon des axes libres (centres de coût, projets, départements, régions) et le suivi budgétaire avec comparaison réel/budget. Offrir une vision de gestion complémentaire à la comptabilité générale.

## 8.2 Sous-modules

| Code | Sous-module |
|------|------------|
| ANA-AXE | Axes et sections analytiques |
| ANA-VEN | Ventilation analytique |
| ANA-EDI | Éditions analytiques |
| BUD-CRE | Création de budgets |
| BUD-SUI | Suivi budgétaire |

## 8.3 Cycle analytique (FOCUS)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CYCLE ANALYTIQUE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. PARAMÉTRAGE                                                  │
│     ├── Création des axes (ex: Centre de coût, Projet)          │
│     ├── Création des sections par axe                            │
│     │   (ex: Marketing, R&D, Production)                        │
│     └── Règles de ventilation par défaut par compte              │
│                                                                  │
│  2. VENTILATION (à la saisie comptable)                         │
│     ├── Manuelle : l'utilisateur choisit la/les section(s)     │
│     ├── Automatique : règle par défaut appliquée                │
│     └── IA assistée : suggestion basée sur l'historique         │
│                                                                  │
│  3. ANALYSE                                                      │
│     ├── Balance analytique par axe/section                      │
│     ├── Grand livre analytique                                  │
│     ├── Reporting croisé multi-axes                             │
│     └── Comparaison réel vs budget                              │
│                                                                  │
│  4. CLÉS DE RÉPARTITION                                         │
│     ├── Charges indirectes réparties selon des clés             │
│     └── Ex: loyer réparti au prorata des m² par département    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 8.4 Fonctionnalités détaillées

### 8.4.1 Ventilation analytique

Chaque ligne d'écriture comptable peut être ventilée sur un ou plusieurs axes analytiques.

**Structure de ventilation** :

```
LigneÉcriture (débit 61110 Achats marchandises, 10 000 MAD)
└── Ventilations analytiques :
    ├── Axe "Centre de coût" :
    │   ├── Section "Production" : 60% = 6 000 MAD
    │   └── Section "Commercial" : 40% = 4 000 MAD
    └── Axe "Projet" :
        ├── Section "Projet Alpha" : 70% = 7 000 MAD
        └── Section "Projet Beta"  : 30% = 3 000 MAD
```

**Règles** :
- La ventilation sur un axe doit totaliser 100% du montant de la ligne.
- Chaque axe est indépendant (la ventilation sur l'axe "Centre de coût" n'impacte pas la ventilation sur l'axe "Projet").
- Maximum 5 axes simultanés.

### 8.4.2 Budgets

**Structure budgétaire** :
- Un budget est défini par : exercice, version (V1, V2 = révision), axe analytique (optionnel), compte comptable.
- Saisie par période (mois) : répartition linéaire (1/12) ou saisonnière (montants libres par mois).
- Import Excel possible.

**Suivi** :
- Pour chaque ligne budgétaire : budget, réel (somme des écritures comptables), écart en valeur, écart en %.
- Alertes configurables : 80% consommé (warning), 100% dépassé (alerte).

## 8.5 Objets métier

| Objet | Description |
|-------|-------------|
| `AxeAnalytique` | Définition d'un axe (centre de coût, projet, etc.) |
| `SectionAnalytique` | Section d'un axe (Marketing, Projet A, etc.) |
| `VentilationAnalytique` | Lien écriture → section avec montant/% |
| `RègleVentilation` | Règle par défaut par compte (ex: compte 612 → 100% Admin) |
| `CléRépartition` | Règle de répartition des charges indirectes |
| `Budget` | Budget pour un exercice + version |
| `LigneBudget` | Montant budgété par compte × section × mois |

## 8.6 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Configuration des axes** | CRUD des axes et sections |
| **Règles de ventilation** | Configuration des règles par défaut |
| **Balance analytique** | Soldes par axe/section avec filtres |
| **Reporting croisé** | Tableau croisé multi-axes |
| **Saisie budgétaire** | Grille de saisie par mois/compte/section |
| **Suivi budgétaire** | Tableau réel vs budget avec écarts |

## 8.7 Obligatoire en MVP

Le module analytique et budgets est prévu en V2/V4 :
- V2 : axes analytiques, sections, ventilation manuelle, balance analytique
- V4 : budgets, suivi budgétaire, clés de répartition, reporting croisé

---

# 9. Reporting & Pilotage

## 9.1 Objectif métier

Fournir des tableaux de bord et des états de synthèse permettant aux dirigeants, experts-comptables et RAF de piloter l'activité en temps réel. Offrir une vue multi-dossiers pour les cabinets comptables et une vue consolidée pour les groupes.

## 9.2 Sous-modules

| Code | Sous-module |
|------|------------|
| RPT-DAS | Dashboards |
| RPT-FIN | Reporting financier |
| RPT-CAB | Pilotage cabinet |
| RPT-EXP | Export & Planification |

## 9.3 Fonctionnalités détaillées

### 9.3.1 Dashboards

**Dashboard dirigeant (PME)** :

| Indicateur | Source | Calcul |
|-----------|--------|--------|
| Chiffre d'affaires du mois | MOD-COM / Classe 71 | Σ des comptes 711x pour la période |
| Résultat courant | MOD-COMPTA | Σ(classe 7) - Σ(classe 6) |
| Trésorerie | MOD-COMPTA | Solde classe 5 |
| Créances clients | MOD-COMPTA | Solde débiteur 3421 |
| Dettes fournisseurs | MOD-COMPTA | Solde créditeur 4411 |
| Masse salariale | MOD-PAIE | Σ brut de la période |
| Stock valorisé | MOD-COM | Σ valorisation CMUP |
| TVA du mois | MOD-TVA | Collectée - Déductible |
| BFR | MOD-COMPTA | Actif circulant HT - Passif circulant HT |
| Évolution CA (graphe 12 mois) | MOD-COMPTA | CA mensuel glissant |

**Dashboard cabinet** :

| Indicateur | Source | Calcul |
|-----------|--------|--------|
| Dossiers en retard de clôture | MOD-COMPTA | Exercice N-1 non clôturé |
| Déclarations TVA en retard | MOD-TVA | Période sans déclaration validée |
| Bulletins de paie non générés | MOD-PAIE | Période ouverte sans validation |
| Dossiers par collaborateur | SOC-IAM | Affectations dossier ↔ utilisateur |
| Avancement par dossier | Tous | % de travaux complétés sur la checklist standard |
| Échéances fiscales | MOD-TVA / MOD-FIS | Dates limites de dépôt |

### 9.3.2 Ratios financiers

| Ratio | Formule | Source |
|-------|---------|--------|
| Rentabilité nette | Résultat net / CA | CPC |
| Marge brute | (Ventes - Achats revendus) / Ventes | CPC |
| Liquidité générale | Actif circulant / Passif circulant | Bilan |
| Liquidité immédiate | Trésorerie / Passif circulant | Bilan |
| Solvabilité | Capitaux propres / Total passif | Bilan |
| Autonomie financière | Capitaux propres / Dettes | Bilan |
| Rotation des stocks | Achats / Stock moyen | CPC + Bilan |
| Délai clients | (Créances clients / CA TTC) × 360 | Bilan + CPC |
| Délai fournisseurs | (Dettes fournisseurs / Achats TTC) × 360 | Bilan + CPC |
| BFR en jours de CA | BFR / (CA / 360) | Bilan + CPC |
| FRNG | Financement permanent - Actif immobilisé | Bilan |

## 9.4 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Dashboard dirigeant** | Widgets KPI configurables, graphes d'évolution |
| **Dashboard cabinet** | Vue multi-dossiers avec avancement, alertes |
| **Ratios financiers** | Tableau de ratios avec comparaison N/N-1, graphes |
| **Constructeur de rapports** | Filtres, regroupements, formules personnalisées (V4) |
| **Planification** | Programmation d'envoi automatique de rapports (V4) |

## 9.5 Obligatoire en MVP

- Dashboard dirigeant avec indicateurs clés
- Dashboard cabinet multi-dossiers
- Comparaison N/N-1 sur tous les états
- Export PDF/Excel

## 9.6 Ce qui peut venir après

- Ratios financiers (V2)
- Consolidation multi-sociétés (V4)
- Constructeur de rapports personnalisé (V4)
- Planification de rapports (V4)

---

# 10. Gestion Documentaire

## 10.1 Objectif métier

Centraliser le stockage, le classement et la recherche de tous les documents justificatifs (factures, relevés bancaires, contrats, bulletins de paie) avec un lien direct vers les objets métier (écriture comptable, bulletin, facture). La GED est le socle pour l'OCR et l'assistance IA.

## 10.2 Sous-modules

| Code | Sous-module |
|------|------------|
| GED-STO | Stockage cloud |
| GED-CLA | Classement & Indexation |
| GED-OCR | OCR et extraction |
| GED-REC | Recherche |
| GED-POR | Portail client |

## 10.3 Cycle de validation documentaire assistée par IA (FOCUS)

```
┌─────────────────────────────────────────────────────────────────┐
│        CYCLE DE VALIDATION DOCUMENTAIRE ASSISTÉE PAR IA          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. RÉCEPTION DU DOCUMENT                                        │
│     ├── Upload manuel (drag-and-drop)                           │
│     ├── Email entrant (boîte de réception automatisée)          │
│     ├── Scan mobile (appareil photo)                            │
│     └── Portail client (dépôt par le client du cabinet)         │
│         Formats : PDF, JPG, PNG, TIFF                           │
│                                                                  │
│  2. TRAITEMENT IA                                                │
│     ├── 2.1 OCR (Reconnaissance de texte)                       │
│     │   └── Extraction du texte brut du document                │
│     │                                                            │
│     ├── 2.2 Classification automatique                          │
│     │   ├── Type : facture achat / facture vente / relevé       │
│     │   │         bancaire / bulletin / contrat / autre         │
│     │   └── Score de confiance (0-100%)                         │
│     │                                                            │
│     ├── 2.3 Extraction structurée (si facture)                  │
│     │   ├── Fournisseur / Client (nom, ICE)                    │
│     │   ├── Date de facture                                     │
│     │   ├── Numéro de facture                                   │
│     │   ├── Montant HT                                          │
│     │   ├── Taux et montant TVA                                 │
│     │   ├── Montant TTC                                         │
│     │   └── Score de confiance par champ                        │
│     │                                                            │
│     └── 2.4 Suggestion d'imputation comptable                   │
│         ├── Compte de charge/produit suggéré                    │
│         ├── Compte de tiers suggéré                             │
│         ├── Compte de TVA suggéré                               │
│         └── Score de confiance global                           │
│                                                                  │
│  3. REVUE HUMAINE                                                │
│     ├── Si confiance > 90% : pré-remplissage, opt-out          │
│     ├── Si confiance 70-90% : suggestion, opt-in               │
│     └── Si confiance < 70% : saisie manuelle                   │
│                                                                  │
│  4. VALIDATION                                                   │
│     ├── L'utilisateur confirme ou corrige                       │
│     ├── L'écriture comptable est créée                          │
│     └── Le document est lié à l'écriture                        │
│                                                                  │
│  5. APPRENTISSAGE                                                │
│     ├── Les corrections de l'utilisateur alimentent le modèle   │
│     └── La confiance augmente au fil du temps pour ce dossier   │
│                                                                  │
│  6. ARCHIVAGE                                                    │
│     ├── Document stocké dans le cloud (S3)                      │
│     ├── Indexé pour la recherche plein texte                    │
│     ├── Lié à l'objet métier (écriture, bulletin, facture)     │
│     └── Conservation 10 ans minimum                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 10.4 Objets métier

| Objet | Attributs clés |
|-------|---------------|
| `Document` | id, tenant_id, dossier_id, nom_fichier, type_mime, taille, chemin_stockage, type_document, statut, texte_ocr, métadonnées_extraites, date_upload, uploadé_par |
| `LienDocument` | id, document_id, objet_type (écriture/bulletin/facture/salarié), objet_id |
| `RésultatOCR` | id, document_id, texte_brut, champs_extraits[], scores_confiance[], modèle_version |

## 10.5 Règles métier

| ID | Règle |
|----|-------|
| GED-R01 | Un document ne peut être supprimé que si aucun objet métier n'y est lié. Sinon, soft-delete uniquement. |
| GED-R02 | Conservation minimale 10 ans (obligation légale marocaine). |
| GED-R03 | L'OCR ne modifie jamais le document original. L'extraction est stockée en métadonnées. |
| GED-R04 | Les documents confidentiels (bulletins de paie) ne sont accessibles qu'aux utilisateurs avec le droit Paie. |

## 10.6 Obligatoire en MVP

- Upload et stockage cloud
- Lien document ↔ écriture comptable
- Recherche par nom, date, type
- Prévisualisation PDF/image

## 10.7 Ce qui peut venir après

- OCR + extraction IA (V2)
- Classification automatique (V2)
- Recherche plein texte (V2)
- Portail client (V4)
- Versioning documents (V4)

---

# 11. Notifications

## 11.1 Objectif métier

Alerter les utilisateurs des événements importants, des échéances réglementaires, des anomalies détectées et des actions requises. Les notifications réduisent le risque de manquement aux obligations et accélèrent les workflows collaboratifs.

## 11.2 Types de notifications

| Catégorie | Exemples | Canaux | Priorité |
|-----------|----------|--------|----------|
| **Échéances réglementaires** | Déclaration TVA due dans 5 jours, état 9421 avant le 28/02, liasse fiscale avant le 31/03 | In-app, Email | Haute |
| **Paie** | Fin de CDD dans 30 jours, fin de période d'essai, congés non pris | In-app, Email | Moyenne |
| **Commercial** | Facture en retard de paiement, stock minimum atteint, devis expirant | In-app | Moyenne |
| **Comptabilité** | Écriture en brouillard depuis 7 jours, rapprochement bancaire en retard, anomalie IA détectée | In-app | Moyenne |
| **Sécurité** | Connexion depuis un nouvel appareil, tentatives échouées, changement de mot de passe | Email, In-app | Haute |
| **Système** | Mise à jour réglementaire disponible, maintenance planifiée, sauvegarde effectuée | In-app | Basse |
| **Workflow** | Demande de congé à approuver, écriture à valider, clôture en attente de validation | In-app, Email | Haute |

## 11.3 Objets métier

| Objet | Attributs |
|-------|-----------|
| `Notification` | id, utilisateur_id, catégorie, titre, message, lien_action, priorité, lue, date_création, date_lecture |
| `PréférenceNotification` | utilisateur_id, catégorie, canal_email (oui/non), canal_inapp (oui/non), fréquence |
| `RègleNotification` | id, événement_déclencheur, condition, template_message, canaux, priorité |

## 11.4 Écrans

| Écran | Description |
|-------|-------------|
| **Centre de notifications** | Liste chronologique avec filtres par catégorie, lu/non lu |
| **Badge de notification** | Compteur dans le header global |
| **Préférences** | Configuration par catégorie (activer/désactiver, canaux) |

## 11.5 Obligatoire en MVP

- Notifications in-app (échéances, sécurité)
- Centre de notifications
- Préférences basiques

## 11.6 Ce qui peut venir après

- Notifications email (V2)
- Notifications de workflow (V2)
- Alertes IA (V3)
- Push notifications PWA (V4)

---

# 12. Audit & Traçabilité

## 12.1 Objectif métier

Garantir une traçabilité complète et immuable de toutes les actions effectuées dans le système. L'audit trail est un pilier de la conformité comptable et fiscale marocaine, et il sert de preuve en cas de contrôle fiscal, d'audit externe ou de litige.

## 12.2 Fonctionnalités détaillées

### 12.2.1 Événements tracés

| Catégorie | Événements |
|-----------|-----------|
| **Authentification** | Connexion, déconnexion, échec de connexion, activation MFA, changement de mot de passe |
| **Comptabilité** | Création/modification/validation/extourne d'écriture, lettrage, délettrage, rapprochement |
| **Paie** | Modification fiche salarié, calcul de paie, validation, modification de rubrique |
| **TVA/Fiscal** | Calcul TVA, validation déclaration, génération liasse, génération EDI |
| **Commercial** | Création/modification/émission de documents, mouvements de stock, inventaire |
| **Immobilisations** | Création, modification, dotation, cession, mise au rebut |
| **Administration** | Création/modification d'utilisateur, modification de rôle, affectation de dossier |
| **Clôture** | Verrouillage de période, clôture d'exercice, réouverture, génération d'à-nouveaux |
| **GED** | Upload, suppression, lien/délien de document |

### 12.2.2 Structure d'un enregistrement d'audit

| Champ | Description |
|-------|-------------|
| `id` | UUID unique |
| `timestamp` | Horodatage UTC précis (millisecondes) |
| `tenant_id` | Identifiant du tenant |
| `dossier_id` | Identifiant du dossier (si applicable) |
| `utilisateur_id` | Identifiant de l'utilisateur |
| `ip_address` | Adresse IP de l'utilisateur |
| `user_agent` | Navigateur / Client |
| `module` | Module concerné (COMPTA, PAIE, COM, etc.) |
| `action` | Type d'action (CREATE, UPDATE, DELETE, VALIDATE, etc.) |
| `objet_type` | Type d'objet (écriture, salarié, facture, etc.) |
| `objet_id` | Identifiant de l'objet |
| `données_avant` | JSON snapshot des données avant modification |
| `données_après` | JSON snapshot des données après modification |
| `métadonnées` | Contexte additionnel (motif de réouverture, etc.) |

### 12.2.3 Propriétés du journal d'audit

- **Immuable** : aucun enregistrement ne peut être modifié ou supprimé, jamais.
- **Append-only** : seules les écritures en ajout sont possibles.
- **Horodatage fiable** : horodatage serveur UTC, non modifiable par l'utilisateur.
- **Consultable** : interface de consultation avec filtres par période, utilisateur, module, action, objet.
- **Exportable** : export en CSV pour les audits externes.
- **Rétention** : conservation minimale 10 ans.

## 12.3 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Journal d'audit** | Liste chronologique avec filtres avancés |
| **Historique d'un objet** | Vue de toutes les modifications d'un objet spécifique (ex : toutes les modifications d'une fiche salarié) |
| **Rapport d'audit** | Rapport généré par période pour audit externe |

## 12.4 Obligatoire en MVP

- Audit trail complet pour tous les événements comptables
- Audit trail pour authentification et administration
- Interface de consultation avec filtres
- Immuabilité garantie (table append-only)
- Export CSV

---

# 13. IA Intégrée

## 13.1 Objectif métier

Fournir une couche d'intelligence artificielle transverse qui accélère les tâches répétitives, réduit les erreurs humaines, détecte les anomalies et assiste les utilisateurs dans leurs décisions. L'IA ne remplace jamais le jugement humain sur les actions officielles.

## 13.2 Sous-modules

| Code | Sous-module | Description |
|------|------------|-------------|
| IA-OCR | OCR & Extraction | Reconnaissance de texte et extraction structurée de factures |
| IA-CLA | Classification | Classification automatique des documents |
| IA-IMP | Suggestion d'imputation | Proposition de comptes comptables |
| IA-ANO | Détection d'anomalies | Identification des écritures, montants ou patterns suspects |
| IA-LET | Assistance au lettrage | Proposition de rapprochement factures/règlements |
| IA-RAP | Assistance au rapprochement | Rapprochement bancaire intelligent |
| IA-CLO | Assistance à la clôture | Checklist intelligente, suggestions de régularisation |
| IA-PRE | Prédiction de trésorerie | Prévision basée sur l'historique |
| IA-ASS | Assistant contextuel | Chatbot interne pour questions métier |

## 13.3 Fonctionnalités détaillées par capacité IA

### 13.3.1 OCR & Extraction (IA-OCR)

**Input** : document PDF ou image (facture fournisseur/client).

**Traitement** :
1. Pré-traitement image (redressement, débruitage, binarisation).
2. OCR pour extraction du texte brut.
3. NLP / modèle de détection d'entités pour extraction structurée :
   - Émetteur (raison sociale, ICE, IF)
   - Destinataire
   - Date de facture
   - Numéro de facture
   - Lignes de facturation (désignation, quantité, prix unitaire)
   - Montant HT total
   - Détail TVA (taux, montant)
   - Montant TTC

**Output** : structure JSON avec chaque champ et son score de confiance.

**Score de confiance** :

| Niveau | Seuil | Comportement UI |
|--------|-------|-----------------|
| Haute confiance | > 90% | Champ pré-rempli, fond vert |
| Moyenne confiance | 70-90% | Champ pré-rempli, fond jaune, demande de validation |
| Basse confiance | < 70% | Champ vide ou grisé, saisie manuelle requise |

### 13.3.2 Suggestion d'imputation (IA-IMP)

**Algorithme** :
1. Historique : recherche des écritures passées avec le même fournisseur/client → compte le plus fréquent.
2. Texte : analyse du libellé de la facture (NLP) → correspondance avec la nomenclature CGNC.
3. Montant : le montant peut indiquer le type de charge (petits montants récurrents = fournitures, gros montant unique = immobilisation).
4. Combinaison : score pondéré des 3 signaux.

**Apprentissage** : chaque validation/correction par l'utilisateur renforce le modèle pour le dossier.

### 13.3.3 Détection d'anomalies (IA-ANO)

| Anomalie | Méthode de détection | Module |
|----------|---------------------|--------|
| Doublon d'écriture | Hash (tiers + montant + date ± 3 jours) | COMPTA |
| Montant inhabituel | Écart-type sur les montants par compte | COMPTA |
| Compte inhabituel | Fréquence historique de l'imputation pour ce tiers | COMPTA |
| TVA incohérente | Montant TVA ≠ Base HT × Taux | TVA |
| Salaire anormalement élevé/bas | Comparaison avec la moyenne par catégorie | PAIE |
| Stock négatif | Quantité en stock < 0 | COM |
| Facture sans règlement (> 90j) | Ancienneté de la créance | COM |
| Écriture en brouillard ancienne | Écriture brouillard > 30 jours | COMPTA |

## 13.4 Règles de gouvernance IA

| Principe | Description |
|----------|-------------|
| **Transparence** | Chaque suggestion IA est accompagnée d'un score de confiance et d'une explication ("Basé sur 42 écritures similaires avec le fournisseur X"). |
| **Contrôle humain** | L'IA ne valide, ne clôture, ne dépose et ne supprime jamais seule. |
| **Apprentissage contextualisé** | Le modèle apprend par dossier (les patterns d'un restaurant sont différents de ceux d'une société de conseil). |
| **Opt-out** | L'utilisateur peut désactiver les suggestions IA par module ou globalement. |
| **Audit** | Chaque suggestion IA et chaque acceptation/rejet est tracé dans l'audit trail. |

## 13.5 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Saisie avec IA** | Zone de drop + preview OCR + formulaire pré-rempli + indicateurs de confiance |
| **Centre d'anomalies** | Liste des anomalies détectées, classées par gravité, avec liens vers les objets |
| **Paramétrage IA** | Activation/désactivation par module, seuils de confiance, modèle de scoring |
| **Assistant IA** (V4) | Chatbot contextuel pour questions ("Pourquoi mon bilan ne s'équilibre pas ?") |

## 13.6 Obligatoire en MVP

L'IA n'est pas obligatoire en MVP (V1). Les premières fonctionnalités IA arrivent en V2 :
- V2 : OCR basique, suggestion d'imputation, détection de doublons
- V3 : Classification automatique, assistance au lettrage et rapprochement
- V4 : Prédiction de trésorerie, assistant contextuel, anomalies avancées

---

# 14. Moteur de Règles Métier

## 14.1 Objectif métier

Centraliser toutes les règles métier réglementaires (barème IR, taux CNSS, taux TVA, durées d'amortissement, SMIG, etc.) dans un composant configurable, versionné et auditable. Permettre la mise à jour des règles sans déploiement logiciel, avec date d'effet et historique complet.

## 14.2 Sous-modules

| Code | Sous-module |
|------|------------|
| RGL-NAT | Règles nationales (réglementaires) |
| RGL-ENT | Règles entreprise (paramétrables) |
| RGL-MOT | Moteur d'exécution |
| RGL-VER | Versioning & Historique |
| RGL-ADM | Administration des règles |

## 14.3 Fonctionnalités détaillées

### 14.3.1 Catalogue des règles

**Règles nationales (non modifiables par l'utilisateur, mises à jour par l'éditeur)** :

| Domaine | Règle | Type | Paramètres |
|---------|-------|------|-----------|
| IR | Barème progressif IR | Table de tranches | Tranches, taux, sommes à déduire |
| IR | Frais professionnels | Taux plafonné | 20%, plafond 2 500 MAD/mois |
| IR | Déduction personnes à charge | Montant fixe | 30 MAD/personne/mois, max 6 |
| CNSS | Taux cotisations | Table de taux | Part salariale, patronale, plafond |
| CNSS | Plafond CNSS | Montant | 6 000 MAD/mois |
| CNSS | Allocations familiales | Taux | 6,40% patronal |
| AMO | Taux AMO | Taux | 2,26% salarial, 4,52% patronal |
| TVA | Taux de TVA | Table de taux | 20%, 14%, 10%, 7%, 0% |
| TVA | Seuil régime mensuel/trimestriel | Montant | 1 000 000 MAD CA |
| TVA | Décalage TVA déductible | Durée | 1 mois |
| SMIG | SMIG horaire | Montant | Montant en vigueur |
| Ancienneté | Barème prime d'ancienneté | Table | Tranches d'ancienneté + taux |
| HS | Taux heures supplémentaires | Table | Jour 25%, nuit 50%, repos 100% |
| Amortissement | Durées par catégorie | Table | Catégorie CGNC → durée de vie standard |
| Amortissement | Coefficients dégressifs | Table | Durée → coefficient |
| IS | Taux IS | Table de tranches | Tranches + taux |
| IS | Cotisation minimale | Taux | 0,5% |

**Règles entreprise (configurables par l'utilisateur)** :

| Domaine | Règle | Description |
|---------|-------|-------------|
| CIMR | Taux CIMR | Taux salarial et patronal choisis par l'entreprise |
| Mutuelle | Taux mutuelle | Selon le contrat souscrit |
| Paie | Rubriques personnalisées | Formules de calcul spécifiques |
| Congés | Droits supplémentaires | Congés conventionnels au-delà du légal |
| Analytique | Clés de répartition | Règles de ventilation des charges indirectes |
| Commercial | Conditions de paiement | Délais de paiement par défaut |

### 14.3.2 Versioning des règles

Chaque règle est versionnée avec :

| Attribut | Description |
|----------|-------------|
| `id_règle` | Identifiant unique de la règle |
| `version` | Numéro de version incrémental |
| `date_effet` | Date à partir de laquelle cette version est applicable |
| `date_fin` | Date de fin d'application (null si en vigueur) |
| `valeur` | Valeur de la règle (taux, barème, montant) |
| `modifié_par` | Utilisateur ou "SYSTÈME" (mise à jour éditeur) |
| `modifié_le` | Date de modification |
| `motif` | Motif de la modification |

**Principe d'application** : un calcul de paie pour le mois de mars 2026 utilise les règles en vigueur au 31/03/2026 (date d'effet ≤ 31/03/2026 et date de fin nulle ou > 31/03/2026).

### 14.3.3 Moteur d'exécution

```
┌────────────────────────────────────────────────────────┐
│              APPEL DEPUIS UN MODULE MÉTIER              │
│  Ex: PAI-CAL demande "calculer l'IR pour un SNI de     │
│      5 000 MAD/mois, 2 personnes à charge,             │
│      date = 31/03/2026"                                 │
├────────────────────────────────────────────────────────┤
│                                                         │
│  1. Résolution de la règle                              │
│     ├── Chercher règle "BAREME_IR"                     │
│     ├── Filtrer par date_effet ≤ 31/03/2026            │
│     └── Prendre la version la plus récente              │
│                                                         │
│  2. Résolution des paramètres liés                      │
│     ├── Règle "FRAIS_PRO" → 20% plafonné 2500         │
│     ├── Règle "DEDUCTION_CHARGE" → 30 × 2 = 60        │
│     └── Toutes à la même date de référence              │
│                                                         │
│  3. Exécution du calcul                                 │
│     ├── SNI = 5000 − (5000 × 20%) = 4000              │
│     ├── IR brut = barème(4000 × 12) / 12              │
│     └── IR net = IR brut − 60                          │
│                                                         │
│  4. Retour du résultat                                  │
│     └── { ir_mensuel: XX, détail_calcul: {...} }       │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### 14.3.4 API du moteur de règles

| Endpoint | Description |
|----------|-------------|
| `GET /rules/{code}?date={date}` | Récupérer la valeur d'une règle à une date donnée |
| `GET /rules/{code}/history` | Historique de toutes les versions d'une règle |
| `POST /rules/{code}/compute` | Exécuter un calcul basé sur une règle (ex: calculer IR) |
| `PUT /rules/{code}` | Mettre à jour une règle entreprise (avec date d'effet) |
| `GET /rules/domain/{domain}` | Lister toutes les règles d'un domaine (IR, CNSS, TVA) |

## 14.4 Objets métier

| Objet | Description |
|-------|-------------|
| `Règle` | Définition d'une règle (code, intitulé, domaine, type, portée nationale/entreprise) |
| `VersionRègle` | Version d'une règle avec date d'effet, valeur, auteur |
| `BarèmeTranches` | Structure pour les barèmes progressifs (IR, IS) |
| `TableTaux` | Structure pour les tables de taux (CNSS, TVA) |

## 14.5 Règles de gouvernance

| Principe | Description |
|----------|-------------|
| **Règles nationales centralisées** | Mises à jour par l'éditeur (EasyAccounting) via un déploiement de données (pas de code). Tous les tenants reçoivent la mise à jour simultanément. |
| **Règles entreprise isolées** | Chaque tenant/société a ses propres paramètres. Pas d'impact inter-tenant. |
| **Priorité** | Si une règle entreprise existe pour un même code, elle prend la priorité sur la règle nationale. |
| **Audit** | Chaque modification est tracée (qui, quand, quoi, motif). |
| **Non-rétroactivité** | Une modification de règle n'affecte pas les calculs déjà validés (les bulletins validés ne changent pas). |

## 14.6 Écrans / interfaces principales

| Écran | Description |
|-------|-------------|
| **Catalogue des règles** | Liste des règles par domaine avec valeurs en vigueur |
| **Détail d'une règle** | Historique des versions, valeur actuelle, prochaine modification prévue |
| **Configuration entreprise** | Modification des règles entreprise (taux CIMR, mutuelle, etc.) |
| **Notification de mise à jour** | Alerte quand une règle nationale est mise à jour par l'éditeur |

## 14.7 Obligatoire en MVP

- Barème IR avec versioning
- Taux CNSS/AMO avec versioning
- Taux TVA avec versioning
- Durées d'amortissement CGNC
- API de calcul consommée par les modules Paie et TVA
- Interface d'administration des règles entreprise (CIMR, mutuelle)

## 14.8 Ce qui peut venir après

- Interface visuelle d'édition de formules (V3)
- Simulation "what-if" : appliquer un nouveau barème IR à la masse salariale existante avant qu'il ne soit en vigueur (V3)
- Alertes proactives de changement réglementaire (V4)

---

# Annexe A — Matrice de couverture AtlasCompta / AtlasPaie / AtlasCom

## A.1 Couverture AtlasCompta

| Fonctionnalité Atlas | Module EasyAccounting | Statut |
|---------------------|----------------------|--------|
| Paramétrage comptable | CPT-PCM | Couvert |
| Plan comptable marocain | CPT-PCM | Couvert |
| Modèle normal | CPT-PCM | Couvert |
| Modèle simplifié | CPT-PCM | Couvert |
| Journaux | CPT-JRN | Couvert |
| Exercices | CPT-EXR / CLO | Couvert |
| À-nouveaux | CLO-ANV | Couvert |
| Clôture | CLO-DEF | Couvert |
| Multi-dossiers | SOC-ORG | Couvert |
| Multi-sociétés | SOC-ORG | Couvert |
| Droits d'accès | SOC-IAM | Couvert |
| Saisie comptable | CPT-ECR | Couvert |
| Import Excel | CPT-ECR | Couvert |
| Modèles d'écriture | CPT-ECR | Couvert |
| Duplication | CPT-ECR | Couvert |
| Équilibre des écritures | CPT-ECR | Couvert |
| TVA | TVA-* | Couvert |
| Immobilisations | IMO-* | Couvert |
| Analytique | ANA-* | Couvert |
| Budgets | BUD-* | Couvert |
| Liasse fiscale | FIS-LIA | Couvert |
| EDI XML | FIS-EDI | Couvert |
| Journal (édition) | CPT-EDT | Couvert |
| Grand livre | CPT-EDT | Couvert |
| Balance | CPT-EDT | Couvert |
| Bilan | CPT-EDT | Couvert |
| CPC | CPT-EDT | Couvert |
| États TVA | TVA-DEC | Couvert |
| Export PDF/Excel | CPT-EDT | Couvert |
| Utilisateurs | SOC-IAM | Couvert |
| Rôles | SOC-IAM | Couvert |

## A.2 Couverture AtlasPaie

| Fonctionnalité Atlas | Module EasyAccounting | Statut |
|---------------------|----------------------|--------|
| Salariés | PAI-SAL | Couvert |
| Informations contractuelles | PAI-SAL | Couvert |
| Historique salaires | PAI-SAL | Couvert |
| Catégories professionnelles | PAI-SAL | Couvert |
| Brut / Net | PAI-CAL | Couvert |
| Net vers brut | PAI-SIM | Couvert |
| Brut vers net | PAI-SIM | Couvert |
| Primes | PAI-RUB | Couvert |
| Retenues | PAI-RUB | Couvert |
| Salariés mensuels/quinzaine/hebdo | PAI-CAL | Couvert |
| Rubriques de paie | PAI-RUB | Couvert |
| Heures supplémentaires | PAI-RUB | Couvert |
| Rubriques personnalisées | PAI-RUB | Couvert |
| Cotisations CNSS/CIMR/mutuelles | PAI-CAL | Couvert |
| Congés | PAI-CON | Couvert |
| Absences | PAI-CON | Couvert |
| Prêts salariés | PAI-PRT | Couvert |
| IR | PAI-CAL | Couvert |
| Régularisation annuelle | PAI-CAL | Couvert |
| Bulletins | PAI-BUL | Couvert |
| DAMANCOM | PAI-DEC | Couvert |
| État 9421 | PAI-DEC | Couvert |
| Atlas BDS | PAI-DEC | Couvert |
| Import Excel/TXT | PAI-SAL | Couvert |
| Conversion XML | PAI-DEC | Couvert |

## A.3 Couverture AtlasCom

| Fonctionnalité Atlas | Module EasyAccounting | Statut |
|---------------------|----------------------|--------|
| Clients | COM-REF | Couvert |
| Produits | COM-REF | Couvert |
| Familles produits | COM-REF | Couvert |
| Codes-barres | COM-REF | Couvert |
| Prix | COM-REF | Couvert |
| Commandes | COM-VTE | Couvert |
| Suivi commandes | COM-VTE | Couvert |
| Facturation | COM-VTE | Couvert |
| Export PDF | COM-VTE | Couvert |
| Impression | COM-VTE | Couvert |
| Paiements / Règlements | COM-RGL | Couvert |
| Encaissements | COM-RGL | Couvert |
| Stock | COM-STK | Couvert |
| Entrées / Sorties | COM-STK | Couvert |
| Inventaire | COM-STK | Couvert |
| Impression Bluetooth/WiFi | COM-VTE | Couvert (V4) |
| Recherche clients/produits | COM-REF | Couvert |
| Scan code-barres | COM-REF | Couvert (V4) |

---

# Annexe B — Matrice des interactions inter-modules

```
            SOC  CPT  TVA  CLO  PAI  COM  IMO  ANA  BUD  RPT  GED  NOT  AUD  IA   RGL
 SOC  ───    ●    ●    ●    ●    ●    ●    ●    ●    ●    ●    ●    ●    ●    ●
 CPT         ───  ●●   ●●        ●    ●    ●    ●    ●    ●         ●    ●    ●
 TVA              ───  ●              ●                   ●         ●    ●    ●
 CLO                   ───  ●    ●    ●                        ●    ●
 PAI                        ───  ●              ●    ●    ●    ●    ●    ●    ●●
 COM                             ───       ●         ●    ●    ●    ●    ●
 IMO                                  ───            ●    ●         ●    ●    ●
 ANA                                       ───  ●    ●                   ●
 BUD                                            ───  ●                   ●
 RPT                                                 ───
 GED                                                      ───       ●    ●
 NOT                                                           ───
 AUD                                                                ───
 IA                                                                      ───
 RGL                                                                          ───

Légende : ● = interaction standard, ●● = interaction forte (flux de données critiques)
```

---

# Annexe C — Roadmap de livraison par domaine

| Domaine | V1 (MVP) | V2 | V3 | V4 |
|---------|----------|-----|-----|-----|
| **Socle Plateforme** | Multi-tenant, multi-dossiers, IAM, import Excel | API publique, import Sage | SSO, multi-langue | Portail client |
| **Comptabilité** | Saisie, lettrage, rapprochement, éditions, liasse, EDI | Saisie IA, récurrence, multi-devises | — | — |
| **TVA & Fiscalité** | Calcul TVA, déclarations, liasse, EDI XML | Prorata, contrôle IA | Assistance IS | Dépôt auto EDI |
| **Clôture** | Périodes, pré-clôture, clôture, à-nouveaux, réouverture | À-nouveaux provisoires, clôture IA | Clôture multi-dossiers en masse | — |
| **Paie** | — | Paie complète + intégration compta | Rubriques avancées, multi-établissements | Portail salarié |
| **Gestion Commerciale** | — | — | Cycle vente + achat + stock + intégration | Grilles de prix, mobile |
| **Immobilisations** | Fiches, amortissements, dotations, cessions, liasse | Amortissement exceptionnel | Réévaluation | — |
| **Analytique** | — | Axes, sections, ventilation, balance | — | Clés répartition, croisé |
| **Budgets** | — | — | — | Budgets complets |
| **Reporting** | Dashboards dirigeant + cabinet | Ratios financiers | — | Constructeur rapports |
| **GED** | Stockage, lien écritures | OCR IA, classif. auto | Recherche plein texte | Portail client, versioning |
| **Notifications** | In-app basiques | Email, workflow | Alertes IA | Push PWA |
| **Audit** | Trail complet, consultation, export | — | — | — |
| **IA** | — | OCR, suggestions, doublons | Lettrage IA, rapprochement IA | Prédiction, assistant |
| **Moteur de règles** | Barèmes IR/CNSS/TVA, amortissements, API | — | Éditeur visuel, simulation | Alertes réglementaires |

---

*Ce document constitue l'architecture fonctionnelle de référence pour EasyAccounting. Il sert de base à l'architecture technique (software architecture document), à la conception UX et au backlog produit.*

*Document vivant — à mettre à jour au fil des sprints.*

---

**EasyAccounting** — *L'architecture d'un ERP pensé pour le Maroc.*
