# EASYACCOUNTING — Backlog Produit & Roadmap

## ERP SaaS marocain unifié — Plan d'exécution structuré

**Version** : 1.0
**Date** : 18 mars 2026
**Statut** : Draft initial
**Références** : PRD v1.0, Architecture Fonctionnelle v1.0, Architecture Technique v1.0
**Classification** : Confidentiel — Usage interne

---

## Table des matières

1. [Stratégie de phasing](#1-stratégie-de-phasing)
2. [Backlog structuré par bloc](#2-backlog-structuré-par-bloc)
   - [Bloc 01 — Socle plateforme](#bloc-01--socle-plateforme)
   - [Bloc 02 — Auth / RBAC](#bloc-02--auth--rbac)
   - [Bloc 03 — Multi-tenant / Organisations / Sociétés / Dossiers](#bloc-03--multi-tenant--organisations--sociétés--dossiers)
   - [Bloc 04 — Exercices / Périodes](#bloc-04--exercices--périodes)
   - [Bloc 05 — Audit & Traçabilité](#bloc-05--audit--traçabilité)
   - [Bloc 06 — Gestion documentaire](#bloc-06--gestion-documentaire)
   - [Bloc 07 — Notifications](#bloc-07--notifications)
   - [Bloc 08 — Comptabilité cœur](#bloc-08--comptabilité-cœur)
   - [Bloc 09 — Imports d'écritures](#bloc-09--imports-décritures)
   - [Bloc 10 — Modèles d'écritures](#bloc-10--modèles-décritures)
   - [Bloc 11 — TVA](#bloc-11--tva)
   - [Bloc 12 — Clôture / Réouverture / À-nouveaux](#bloc-12--clôture--réouverture--à-nouveaux)
   - [Bloc 13 — Lettrage](#bloc-13--lettrage)
   - [Bloc 14 — Rapprochement bancaire](#bloc-14--rapprochement-bancaire)
   - [Bloc 15 — Reporting comptable](#bloc-15--reporting-comptable)
   - [Bloc 16 — Liasse fiscale / EDI](#bloc-16--liasse-fiscale--edi)
   - [Bloc 17 — Paie & RH](#bloc-17--paie--rh)
   - [Bloc 18 — Déclarations sociales](#bloc-18--déclarations-sociales)
   - [Bloc 19 — Gestion commerciale](#bloc-19--gestion-commerciale)
   - [Bloc 20 — Stock](#bloc-20--stock)
   - [Bloc 21 — Immobilisations](#bloc-21--immobilisations)
   - [Bloc 22 — Analytique](#bloc-22--analytique)
   - [Bloc 23 — Budgets](#bloc-23--budgets)
   - [Bloc 24 — Reporting & Dashboards](#bloc-24--reporting--dashboards)
   - [Bloc 25 — IA documentaire](#bloc-25--ia-documentaire)
   - [Bloc 26 — IA assistance métier](#bloc-26--ia-assistance-métier)
   - [Bloc 27 — Moteur de règles](#bloc-27--moteur-de-règles)
   - [Bloc 28 — Qualité / Tests / Sécurité / Observabilité](#bloc-28--qualité--tests--sécurité--observabilité)
3. [Roadmap par phases](#3-roadmap-par-phases)
4. [Matrice des dépendances inter-blocs](#4-matrice-des-dépendances-inter-blocs)
5. [Arbitrages MVP](#5-arbitrages-mvp)

---

# 1. Stratégie de phasing

## 1.1 Définition des phases

| Phase | Nom | Horizon | Objectif stratégique | Cible principale |
|-------|-----|---------|---------------------|------------------|
| **MVP** | Socle + Compta minimale | Mois 0–4 | Démontrer la viabilité technique et la valeur métier minimale. Testable en interne et par 3-5 cabinets pilotes. | Équipe interne, early adopters |
| **V1** | Comptabilité complète | Mois 4–9 | Produit exploitable en production par un cabinet comptable pour la tenue, la déclaration TVA, les immobilisations, le reporting et la liasse fiscale. | Cabinets comptables, experts-comptables indépendants |
| **V2** | + Paie + IA de base | Mois 9–15 | Extension aux fiduciaires et PME avec paie marocaine complète, intégration paie-compta, et premières fonctions IA (OCR, suggestion). | Fiduciaires, PME |
| **V3** | + Commercial + Stock | Mois 15–21 | Extension aux PME commerciales et industrielles avec cycle commercial complet, gestion de stock, et intégration commercial-compta. | PME commerciales, groupes |
| **V4** | + Analytique + Budgets + IA avancée | Mois 21–27 | Plateforme complète avec pilotage financier avancé, consolidation, portail collaboratif, IA mature. | Groupes multi-entités |

## 1.2 Principes d'arbitrage

| Principe | Explication |
|----------|-------------|
| **La comptabilité est le cœur** | Sans module comptable fonctionnel, aucun autre module n'a de valeur. La compta est le noyau sur lequel tout se branche. |
| **Le socle avant les modules** | Auth, multi-tenant, audit, exercices, dossiers doivent exister AVANT toute saisie d'écriture. |
| **Conformité > Confort** | Les obligations réglementaires marocaines (CGNC, TVA, IR, CNSS) passent avant les fonctions de confort. |
| **Intégration > Module isolé** | Un module mal intégré crée de la ressaisie. Chaque module livré doit être connecté au flux comptable. |
| **IA = accélérateur, pas prérequis** | Le produit doit fonctionner à 100% sans IA. L'IA est un accélérateur rajouté par-dessus. |
| **Moteur de règles dès le MVP** | Les paramètres réglementaires (taux TVA, plan comptable) sont des données dès le jour 1. Pas de hardcoding. |

## 1.3 Ce qui DOIT être dans le MVP

- Structure multi-tenant avec RLS
- Auth JWT + MFA pour admins
- RBAC avec rôles prédéfinis
- Gestion tenants / sociétés / dossiers / exercices / périodes
- Plan de comptes marocain (CGNC classes 1-9)
- Journaux et saisie d'écritures (brouillard → validation)
- Tiers (clients / fournisseurs)
- Balance générale, grand livre, journal centraliseur
- Audit log immutable
- Moteur de règles (taux TVA, plan comptable par défaut)
- Infrastructure Docker complète

## 1.4 Ce qui peut ATTENDRE

| Fonctionnalité | Pourquoi ça peut attendre | Phase cible |
|---------------|--------------------------|-------------|
| Paie complète | Module indépendant, pas bloquant pour la compta | V2 |
| Gestion commerciale | Les cabinets comptables n'en ont pas besoin au quotidien | V3 |
| IA (OCR, suggestions) | Le produit fonctionne manuellement sans IA | V2 |
| Analytique / budgets | Reporting avancé, pas critique pour la tenue | V2/V4 |
| Consolidation multi-sociétés | Cas d'usage de groupe, pas de cabinet | V4 |
| SSO SAML/OIDC | Les cabinets utilisent email/password | V3 |
| Portail client / salarié | Fonctionnalité de confort | V4 |

## 1.5 Ce qui est TROP RISQUÉ pour le MVP

| Fonctionnalité | Risque | Mitigation |
|---------------|--------|------------|
| Dépôt EDI automatique à la DGI | Certification DGI requise, specs changeantes | MVP : génération XML, dépôt manuel par l'utilisateur |
| Calcul de paie complet | Complexité IR/CNSS/AMO, risque d'erreur | Décalé en V2 avec validation extensive |
| IA décisionnelle autonome | Risque de confiance prématurée | IA = suggestion uniquement, jamais d'action sans validation humaine |
| Multi-devises avec conversion | Complexité écarts de change, impact bilan | V2 avec conversion manuelle d'abord |
| Import depuis Sage | Formats propriétaires, peu documentés | V2, après stabilisation de l'import Excel |

---

# 2. Backlog structuré par bloc

---

## Bloc 01 — Socle plateforme

### Epic 01.1 : Infrastructure technique de base

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 01.1.1 | Setup projet backend | En tant que développeur, je veux un projet FastAPI structuré en monolithe modulaire pour démarrer le développement | Scaffolding du projet : structure de dossiers par domaine, app factory, configuration par environnement (dev/staging/prod), gestion des settings via Pydantic BaseSettings | - Le serveur FastAPI démarre sans erreur<br>- La structure suit le pattern `app/{domain}/router.py, service.py, repository.py, models.py, schemas.py`<br>- Les variables d'environnement sont chargées via `.env`<br>- Le healthcheck `/api/v1/health` répond 200 | P0 | Aucune | MVP |
| 01.1.2 | Setup projet frontend | En tant que développeur front, je veux un projet Next.js 14+ App Router avec TypeScript, Tailwind et shadcn/ui configurés | Scaffolding frontend : Next.js App Router, TypeScript strict, Tailwind CSS, shadcn/ui, ESLint, Prettier, structure de dossiers par feature | - `npm run dev` démarre sans erreur<br>- TypeScript strict mode activé<br>- shadcn/ui disponible et thème EasyAccounting configuré<br>- Page de login placeholder fonctionnelle | P0 | Aucune | MVP |
| 01.1.3 | Docker Compose complet | En tant que développeur, je veux un docker-compose qui lance tout l'environnement local en une commande | Services : api, frontend, db (PostgreSQL 16), redis, minio, celery-worker. Volumes persistants, hot-reload en dev. | - `docker-compose up` lance tous les services<br>- PostgreSQL accessible sur le port 5432<br>- Redis accessible sur 6379<br>- MinIO accessible sur 9000/9001<br>- Hot-reload fonctionnel sur api et frontend | P0 | 01.1.1, 01.1.2 | MVP |
| 01.1.4 | Configuration Alembic | En tant que développeur, je veux un système de migrations de base de données reproductible | Setup Alembic avec convention de nommage, support multi-tenant, script de migration initial, seed data pour le développement | - `alembic upgrade head` crée toutes les tables<br>- `alembic downgrade -1` fonctionne<br>- Convention de nommage : `{rev}_{slug}.py`<br>- Seed data insère un tenant de test | P0 | 01.1.1 | MVP |
| 01.1.5 | CI/CD pipeline de base | En tant que développeur, je veux un pipeline CI qui valide chaque PR automatiquement | GitHub Actions : lint (ruff + eslint), type-check (mypy + tsc), tests unitaires, build Docker, scan de sécurité basique | - Le pipeline tourne sur chaque push/PR<br>- Lint, type-check, tests exécutés en parallèle<br>- Build Docker réussit<br>- Badge de statut sur le README | P0 | 01.1.1, 01.1.2 | MVP |
| 01.1.6 | Bus d'événements interne | En tant que développeur, je veux un système de publication/souscription d'événements entre modules | Implémentation in-process du pattern event bus : `publish(event)`, `subscribe(event_type, handler)`. Événements typés, handlers asynchrones. | - Un module peut publier un événement<br>- Les modules abonnés reçoivent l'événement<br>- Les handlers s'exécutent de manière asynchrone<br>- Les erreurs dans un handler n'affectent pas les autres<br>- Les événements sont loggés | P1 | 01.1.1 | MVP |

### Epic 01.2 : Paramétrage global

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 01.2.1 | Table des paramètres système | En tant qu'administrateur, je veux configurer les paramètres globaux de la plateforme | Table `Setting` : clé/valeur typée, scopée (global, tenant, société, dossier). Paramètres par défaut : devise MAD, format date JJ/MM/AAAA, fuseau Africa/Casablanca, séparateurs FR | - CRUD des paramètres via API<br>- Cascade de résolution : dossier > société > tenant > global<br>- Paramètres par défaut créés au provisioning<br>- Validation du type de valeur | P0 | 01.1.4 | MVP |
| 01.2.2 | Interface de paramétrage | En tant qu'administrateur, je veux une interface pour gérer les paramètres de ma plateforme | Écran de configuration : onglets par catégorie (Général, Comptabilité, Fiscal, Paie), formulaires de saisie, sauvegarde avec validation | - Interface accessible depuis le menu admin<br>- Onglets par catégorie<br>- Sauvegarde avec feedback visuel<br>- Paramètres appliqués immédiatement | P1 | 01.2.1, 01.1.2 | MVP |

---

## Bloc 02 — Auth / RBAC

### Epic 02.1 : Authentification

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 02.1.1 | Inscription et login | En tant qu'utilisateur, je veux créer un compte et me connecter de manière sécurisée | Endpoints : `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`. Hashage argon2, JWT access (15 min) + refresh (7 jours). | - L'inscription crée un utilisateur et un tenant<br>- Le login retourne un access token et un refresh token<br>- Le refresh renouvelle le token sans re-login<br>- Le logout invalide le refresh token<br>- Les mots de passe sont hashés avec argon2 | P0 | 01.1.1 | MVP |
| 02.1.2 | MFA TOTP | En tant qu'administrateur, je veux activer l'authentification à deux facteurs pour sécuriser mon compte | Endpoints : `POST /auth/mfa/setup`, `POST /auth/mfa/verify`, `POST /auth/mfa/disable`. Compatible Google Authenticator, QR code, codes de secours. | - Activation MFA génère un QR code<br>- Vérification via code TOTP à 6 chiffres<br>- 10 codes de secours générés et affichés une seule fois<br>- MFA obligatoire pour le rôle Administrateur<br>- Verrouillage après 5 tentatives échouées | P0 | 02.1.1 | MVP |
| 02.1.3 | Reset mot de passe | En tant qu'utilisateur, je veux réinitialiser mon mot de passe si je l'oublie | Endpoints : `POST /auth/forgot-password`, `POST /auth/reset-password`. Envoi d'email avec token signé, expiration 1h, usage unique. | - L'email de reset est envoyé en < 30 secondes<br>- Le lien expire après 1 heure<br>- Le lien est usage unique<br>- Le nouveau mot de passe doit respecter la politique de sécurité (8+ caractères, 1 majuscule, 1 chiffre) | P0 | 02.1.1 | MVP |
| 02.1.4 | Gestion des sessions | En tant qu'administrateur, je veux voir et révoquer les sessions actives de mes utilisateurs | Liste des sessions actives (IP, user-agent, dernière activité), révocation unitaire ou totale. | - Liste des sessions avec métadonnées<br>- Révocation immédiate d'une session<br>- Révocation de toutes les sessions sauf la courante<br>- Log d'audit à chaque révocation | P1 | 02.1.1 | MVP |
| 02.1.5 | SSO SAML/OIDC | En tant qu'entreprise, je veux connecter EasyAccounting à mon annuaire d'entreprise | Support SAML 2.0 et OpenID Connect. Configuration par tenant : metadata URL, mapping d'attributs, provisioning automatique des utilisateurs. | - Configuration SSO via interface admin<br>- Login SSO fonctionnel avec redirection<br>- Provisioning JIT des utilisateurs<br>- Fallback sur login local si SSO indisponible | P3 | 02.1.1 | V3 |

### Epic 02.2 : RBAC (Role-Based Access Control)

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 02.2.1 | Modèle rôles et permissions | En tant qu'administrateur, je veux un système de rôles avec des permissions granulaires | Tables : `Role`, `Permission`, `RolePermission`. Rôles prédéfinis : Administrateur, Expert-comptable, Collaborateur, Gestionnaire paie, Commercial, Lecture seule. Matrice Module × Action × Périmètre. | - 6 rôles prédéfinis créés au seed<br>- Chaque rôle a ses permissions par défaut<br>- La matrice couvre : module, action (lire/créer/modifier/supprimer/valider/exporter), périmètre (tous/assignés)<br>- Les rôles prédéfinis ne peuvent pas être supprimés | P0 | 01.1.4 | MVP |
| 02.2.2 | Middleware RBAC | En tant que développeur, je veux que chaque endpoint vérifie automatiquement les permissions | Décorateur/dépendance FastAPI : `@require_permission("compta.ecriture.creer")`. Vérification du rôle de l'utilisateur dans le contexte du dossier courant. | - Chaque endpoint protégé vérifie la permission<br>- Un 403 est retourné si la permission est manquante<br>- Le middleware est performant (< 5ms de surcoût)<br>- Le bypass admin fonctionne pour le super-admin | P0 | 02.2.1, 02.1.1 | MVP |
| 02.2.3 | Rôles personnalisés | En tant qu'administrateur, je veux créer des rôles sur mesure pour mon organisation | Interface de création de rôle : nom, description, sélection des permissions via matrice visuelle (checkboxes par module × action). | - Création d'un rôle personnalisé via interface<br>- Matrice visuelle de permissions avec toggle par module/action<br>- Duplication d'un rôle existant comme base<br>- Suppression d'un rôle personnalisé (avec réaffectation des utilisateurs) | P2 | 02.2.1 | V1 |
| 02.2.4 | Affectation utilisateurs-dossiers | En tant qu'expert-comptable, je veux affecter mes collaborateurs à des dossiers spécifiques | Table `UserDossierAssignment`. Interface d'affectation : sélection utilisateur, sélection dossier(s), rôle dans le dossier. Un collaborateur ne voit que ses dossiers assignés. | - Affectation d'un utilisateur à un ou plusieurs dossiers<br>- Le collaborateur ne voit que ses dossiers dans la liste<br>- Les données des dossiers non assignés sont inaccessibles (vérifié via RLS)<br>- L'expert-comptable et l'admin voient tous les dossiers | P0 | 02.2.1, 03.1.3 | MVP |

---

## Bloc 03 — Multi-tenant / Organisations / Sociétés / Dossiers

### Epic 03.1 : Multi-tenant et structure organisationnelle

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 03.1.1 | Row-Level Security | En tant qu'architecte, je veux une isolation des données par tenant garantie au niveau de la base de données | Politique RLS PostgreSQL sur toutes les tables : `CREATE POLICY tenant_isolation ON {table} USING (tenant_id = current_setting('app.current_tenant')::uuid)`. Middleware FastAPI qui injecte le `tenant_id` du JWT. | - Politique RLS active sur chaque table avec `tenant_id`<br>- Le middleware injecte le tenant_id dans la session PostgreSQL<br>- Un utilisateur du tenant A ne peut JAMAIS accéder aux données du tenant B<br>- Test d'intrusion : requête cross-tenant retourne 0 résultats | P0 | 01.1.4 | MVP |
| 03.1.2 | CRUD Tenant | En tant que super-admin, je veux créer, modifier et suspendre des tenants | Endpoints : CRUD `/admin/tenants`. Statuts : actif, suspendu (lecture seule), gelé, supprimé logiquement. Provisioning automatique (paramètres par défaut, rôles, plan de comptes). | - Création d'un tenant provisionne les données par défaut<br>- Suspension passe le tenant en lecture seule<br>- Gel bloque tout accès<br>- Suppression logique (jamais physique, rétention 10 ans) | P0 | 03.1.1 | MVP |
| 03.1.3 | CRUD Sociétés et dossiers | En tant qu'administrateur, je veux créer des sociétés et des dossiers dans mon espace | Hiérarchie : Tenant → Société(s) → Dossier(s). Société : ICE, IF, RC, patente, CNSS employeur, forme juridique, capital, adresse, logo. Dossier : unité de travail comptable avec son propre plan de comptes et ses journaux. | - Création d'une société avec tous les champs légaux<br>- Création d'un dossier rattaché à une société<br>- Chaque dossier hérite des paramètres de la société par défaut<br>- Basculement de dossier sans rechargement de page<br>- Validation de l'ICE (format marocain) | P0 | 03.1.2 | MVP |
| 03.1.4 | Context switcher | En tant qu'utilisateur, je veux changer de dossier rapidement depuis n'importe quelle page | Composant frontend : dropdown/modal de sélection de dossier, accessible depuis le header. Recherche rapide par nom, ICE, ou code. Le contexte (dossier_id) est stocké dans le state global et envoyé dans chaque requête API. | - Le switcher est accessible depuis toutes les pages<br>- Recherche avec autocomplétion<br>- Changement de dossier en < 500ms<br>- L'URL reflète le dossier courant<br>- Le dernier dossier utilisé est mémorisé | P0 | 03.1.3, 01.1.2 | MVP |
| 03.1.5 | Gestion des établissements | En tant qu'administrateur, je veux gérer les établissements (sites) d'une société | CRUD établissements rattachés à une société. Pertinent pour la paie (CNSS par établissement) et le stock (multi-dépôts). | - Création d'un établissement avec adresse et CNSS<br>- Rattachement à une société<br>- Un établissement ne peut pas être supprimé s'il a des salariés actifs | P2 | 03.1.3 | V2 |

---

## Bloc 04 — Exercices / Périodes

### Epic 04.1 : Gestion des exercices comptables

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 04.1.1 | CRUD exercices fiscaux | En tant que comptable, je veux créer et gérer les exercices fiscaux d'un dossier | Table `FiscalYear`. Création : date début, date fin (12 ou 18 mois max pour le 1er exercice), devise. Statuts : CRÉÉ → OUVERT → PRÉ-CLÔTURE → CLÔTURÉ → RÉOUVERT. Un seul exercice ouvert à la fois. | - Création d'un exercice avec dates et devise<br>- Validation : durée 12 mois (sauf 1er exercice : 18 mois max)<br>- Un seul exercice peut être OUVERT à la fois<br>- Pas de chevauchement de dates entre exercices<br>- Les dates sont contiguës (J+1 du précédent) | P0 | 03.1.3 | MVP |
| 04.1.2 | Gestion des périodes comptables | En tant que comptable, je veux que chaque exercice soit découpé en périodes mensuelles | Table `AccountingPeriod`. Génération automatique des 12 périodes mensuelles à la création de l'exercice + une période d'OD (opérations diverses). Statuts : OUVERTE, VERROUILLÉE, CLÔTURÉE. | - 12 périodes mensuelles + 1 période OD générées automatiquement<br>- Verrouillage d'une période empêche toute nouvelle écriture<br>- Clôture d'une période est irréversible (sauf via réouverture exercice)<br>- Les écritures ne peuvent être saisies que dans une période OUVERTE | P0 | 04.1.1 | MVP |
| 04.1.3 | Verrouillage de période | En tant qu'expert-comptable, je veux verrouiller une période pour interdire toute modification | Action de verrouillage avec confirmation. Seuls les rôles Expert-comptable et Administrateur peuvent verrouiller. Un contrôle de cohérence est lancé avant verrouillage (équilibre des écritures, pièces manquantes). | - Bouton de verrouillage avec confirmation<br>- Contrôle de cohérence pré-verrouillage<br>- Rapport des anomalies bloquantes / warnings<br>- Verrouillage impossible si anomalies bloquantes<br>- Log d'audit du verrouillage | P0 | 04.1.2, 05.1.1 | MVP |

---

## Bloc 05 — Audit & Traçabilité

### Epic 05.1 : Audit log immutable

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 05.1.1 | Enregistrement automatique des actions | En tant qu'auditeur, je veux que toute action modifiant des données soit tracée automatiquement | Table `AuditLog` : partitionnée par mois. Colonnes : id, tenant_id, user_id, action, entity_type, entity_id, old_values (JSONB), new_values (JSONB), ip_address, user_agent, timestamp. INSERT + SELECT uniquement (jamais UPDATE/DELETE). | - Chaque création, modification, suppression est loguée<br>- Les anciennes et nouvelles valeurs sont stockées en JSONB<br>- L'IP et le user-agent sont capturés<br>- La table est partitionnée par mois<br>- Aucune opération UPDATE ou DELETE n'est possible sur la table<br>- Rétention 10 ans | P0 | 01.1.4 | MVP |
| 05.1.2 | Interface de consultation audit | En tant qu'administrateur, je veux consulter l'historique des actions sur un dossier | Écran d'audit : filtres par utilisateur, entité, action, date. Affichage chronologique avec diff visuel (ancien → nouveau). Export CSV. | - Filtrage par utilisateur, entité, action, plage de dates<br>- Diff visuel des modifications (ancien/nouveau)<br>- Pagination performante (> 100k logs)<br>- Export CSV | P1 | 05.1.1 | MVP |
| 05.1.3 | Historique d'une entité | En tant que comptable, je veux voir l'historique complet d'une écriture ou d'un tiers | Onglet "Historique" sur chaque fiche (écriture, tiers, compte, salarié) : liste des modifications avec date, auteur, détail du changement. | - Onglet Historique visible sur chaque entité<br>- Liste chronologique des modifications<br>- Lien vers l'utilisateur qui a fait la modification<br>- Accessible aux rôles Expert-comptable et Admin | P2 | 05.1.1 | V1 |

---

## Bloc 06 — Gestion documentaire

### Epic 06.1 : Stockage et gestion de documents

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 06.1.1 | Upload et stockage MinIO | En tant qu'utilisateur, je veux télécharger des documents et les rattacher à des entités | Service de stockage : upload vers MinIO (S3-compatible), structure de buckets par tenant. Table `Document` : filename, mime_type, size, storage_path, checksum SHA-256. Table `DocumentLink` : entity_type, entity_id → document_id. | - Upload de fichiers jusqu'à 20 Mo<br>- Types acceptés : PDF, JPG, PNG, XLSX, CSV, XML<br>- Vérification antivirus basique (extension + magic bytes)<br>- Checksum SHA-256 calculé et stocké<br>- Stockage dans MinIO avec path : `{tenant_id}/{year}/{month}/{uuid}.{ext}` | P0 | 01.1.3 | MVP |
| 06.1.2 | Rattachement de pièces justificatives | En tant que comptable, je veux rattacher une pièce justificative à une écriture comptable | Zone de drop sur le formulaire d'écriture. Affichage de la miniature/icône des pièces jointes. Lien bidirectionnel : écriture ↔ document(s). | - Drag & drop ou bouton d'upload sur le formulaire d'écriture<br>- Plusieurs pièces par écriture<br>- Prévisualisation PDF/image dans une modale<br>- Téléchargement du document original<br>- Suppression de la liaison (pas du document) | P1 | 06.1.1, 08.1.2 | MVP |
| 06.1.3 | Explorateur de documents | En tant qu'utilisateur, je veux naviguer dans tous les documents d'un dossier | Vue arborescente et vue liste. Filtres : type, date, entité liée, non rattachés. Tri par date, nom, taille. | - Vue liste avec pagination<br>- Filtres par type, date, statut (rattaché/orphelin)<br>- Prévisualisation rapide<br>- Téléchargement unitaire et par lot (ZIP) | P2 | 06.1.1 | V1 |
| 06.1.4 | OCR et extraction IA | En tant que comptable, je veux que le système extraie automatiquement les données d'une facture scannée | Service OCR (Tesseract ou API externe). Extraction : fournisseur, date, montant HT, TVA, TTC, numéro de facture. Création d'une suggestion d'écriture pré-remplie. | - OCR fonctionnel sur PDF et images<br>- Extraction des champs clés avec score de confiance<br>- Suggestion d'écriture pré-remplie soumise à validation humaine<br>- Taux d'extraction correct > 80% sur factures standards marocaines | P2 | 06.1.1, 26.1.1 | V2 |

---

## Bloc 07 — Notifications

### Epic 07.1 : Système de notifications

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 07.1.1 | Notifications in-app | En tant qu'utilisateur, je veux recevoir des notifications dans l'application | Table `Notification` : user_id, type, title, body, read, entity_type, entity_id. Icône cloche avec badge de compteur non-lus. Panneau de notifications avec liste scrollable. | - Icône de notification avec badge non-lus<br>- Panneau déroulant avec liste des notifications<br>- Marquage comme lu unitaire et global<br>- Clic sur une notification navigue vers l'entité liée<br>- Notifications temps réel via polling (SSE en V2) | P1 | 01.1.2 | MVP |
| 07.1.2 | Notifications email | En tant qu'utilisateur, je veux recevoir des alertes importantes par email | Service email (SMTP ou API SendGrid/Mailgun). Templates par type de notification. Préférence utilisateur : opt-in/opt-out par catégorie. | - Envoi d'email pour les notifications critiques<br>- Templates HTML responsive<br>- Lien direct vers l'entité dans l'email<br>- Préférences de notification par utilisateur<br>- Rate limiting pour éviter le spam | P2 | 07.1.1 | V2 |
| 07.1.3 | Notifications de workflow | En tant qu'expert-comptable, je veux être notifié quand un collaborateur soumet une écriture pour validation | Notifications déclenchées par les changements de statut des workflows : soumission d'écriture, validation de bulletin, clôture de période. | - Notification à la soumission d'écriture pour validation<br>- Notification à la validation/rejet<br>- Notification à la clôture de période<br>- Notification à l'échéance TVA (rappel J-5) | P2 | 07.1.1, 01.1.6 | V2 |

---

## Bloc 08 — Comptabilité cœur

### Epic 08.1 : Plan de comptes

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 08.1.1 | Plan de comptes CGNC | En tant que comptable, je veux un plan de comptes marocain (CGNC) initialisé automatiquement à la création d'un dossier | Table `Account` : numéro (VARCHAR 10), libellé, classe (1-9), type (détail/collectif/centralisateur), nature (débit/crédit), is_system, is_lettrable, tva_rate_default. Seed du PCM officiel (classes 1 à 9, modèle normal). | - PCM chargé automatiquement à la création du dossier<br>- Classes 1 à 9 avec sous-comptes standards<br>- Comptes système protégés contre la suppression<br>- Numérotation hiérarchique (3411 est enfant de 341 qui est enfant de 34)<br>- Support modèle normal et simplifié | P0 | 04.1.1, 27.1.1 | MVP |
| 08.1.2 | CRUD comptes | En tant que comptable, je veux ajouter, modifier et consulter des comptes dans le plan | Interface de gestion : vue arborescente et vue liste. Création de comptes auxiliaires sous les comptes collectifs. Recherche par numéro ou libellé. Interdiction de supprimer un compte mouvementé. | - Vue arborescente du plan de comptes<br>- Création d'un compte avec numéro auto-incrémenté ou libre<br>- Modification du libellé (pas du numéro si mouvementé)<br>- Recherche avec autocomplétion<br>- Suppression impossible si le compte a des mouvements | P0 | 08.1.1 | MVP |
| 08.1.3 | Import plan de comptes | En tant que comptable, je veux importer un plan de comptes depuis un fichier Excel | Upload Excel → parsing → validation (numéros uniques, hiérarchie cohérente, classes valides) → preview → confirmation → import. Rapport d'erreurs détaillé. | - Template Excel téléchargeable<br>- Validation stricte avec rapport d'erreurs ligne par ligne<br>- Preview avant import<br>- Import atomique (tout ou rien)<br>- Fusion avec le plan existant (mise à jour + ajout) | P1 | 08.1.1, 09.1.1 | MVP |

### Epic 08.2 : Journaux et écritures

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 08.2.1 | Gestion des journaux | En tant que comptable, je veux créer et configurer les journaux comptables | Table `Journal` : code (unique par dossier), libellé, type (achat, vente, trésorerie, OD, à-nouveaux, situation). Journaux par défaut créés au seed (AC, VE, BQ, OD, AN). | - Journaux par défaut créés automatiquement<br>- Création de journaux personnalisés<br>- Configuration du compte de contrepartie par journal<br>- Numérotation séquentielle par journal et par période<br>- Interdiction de supprimer un journal mouvementé | P0 | 08.1.1 | MVP |
| 08.2.2 | Saisie d'écritures comptables | En tant que comptable, je veux saisir des écritures comptables dans un journal | Formulaire de saisie : date, journal, libellé, lignes (compte, libellé, débit, crédit, tiers optionnel). Contrôles : équilibre débit/crédit, compte existant, période ouverte, montants en NUMERIC(15,2). Statuts : BROUILLARD → VALIDÉE. | - Formulaire de saisie multi-lignes<br>- Autocomplétion du compte et du tiers<br>- Contrôle d'équilibre en temps réel (débit = crédit)<br>- Contrôle de période ouverte<br>- Enregistrement en BROUILLARD par défaut<br>- Montants en NUMERIC(15,2) — jamais de float<br>- Numéro de pièce auto-généré (journal + période + séquence) | P0 | 08.2.1, 04.1.2 | MVP |
| 08.2.3 | Validation d'écritures | En tant qu'expert-comptable, je veux valider les écritures brouillard pour les rendre définitives | Action de validation unitaire et par lot. L'écriture validée est immuable (pas d'UPDATE, pas de DELETE). Contrepassation obligatoire pour corriger une écriture validée. | - Validation unitaire et par lot<br>- L'écriture validée ne peut plus être modifiée<br>- Suppression impossible d'une écriture validée<br>- Seule la contrepassation permet de corriger<br>- Log d'audit à la validation<br>- Seuls Expert-comptable et Admin peuvent valider | P0 | 08.2.2, 02.2.2 | MVP |
| 08.2.4 | Contrepassation | En tant que comptable, je veux contrepasser une écriture validée pour la corriger | Génération automatique de l'écriture inverse (débit ↔ crédit). Lien de référence vers l'écriture d'origine. Saisie de l'écriture corrective dans la foulée (optionnel). | - Génération de l'écriture inverse en un clic<br>- Référence croisée entre écriture d'origine et contrepassation<br>- L'écriture inverse est créée en BROUILLARD<br>- Proposition de saisie de l'écriture corrective | P0 | 08.2.3 | MVP |
| 08.2.5 | Consultation et recherche d'écritures | En tant que comptable, je veux rechercher et consulter les écritures d'un dossier | Vue liste paginée avec filtres : journal, période, compte, tiers, statut, montant, libellé. Tri par date, numéro, montant. Export Excel/CSV. | - Filtres multiples combinables<br>- Recherche full-text sur libellé<br>- Pagination performante (> 100k écritures)<br>- Export Excel et CSV<br>- Affichage des pièces jointes liées | P0 | 08.2.2 | MVP |

### Epic 08.3 : Tiers

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 08.3.1 | Gestion des tiers | En tant que comptable, je veux gérer les clients et fournisseurs du dossier | Table `ThirdParty` : type (client/fournisseur/les deux), raison sociale, ICE, IF, RC, adresse, téléphone, email, compte comptable par défaut, conditions de paiement. | - CRUD complet des tiers<br>- Types : client, fournisseur, client+fournisseur<br>- Champs légaux marocains (ICE, IF, RC)<br>- Compte comptable associé par défaut<br>- Recherche par nom, ICE, IF<br>- Interdiction de supprimer un tiers mouvementé | P0 | 08.1.2 | MVP |
| 08.3.2 | Import tiers depuis Excel | En tant que comptable, je veux importer ma liste de tiers depuis un fichier Excel | Upload → parsing → validation (ICE unique, champs obligatoires) → preview → import. | - Template téléchargeable<br>- Validation stricte<br>- Détection des doublons (par ICE ou raison sociale)<br>- Import atomique avec rapport | P1 | 08.3.1, 09.1.1 | MVP |

---

## Bloc 09 — Imports d'écritures

### Epic 09.1 : Import d'écritures depuis fichiers

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 09.1.1 | Import Excel d'écritures | En tant que comptable, je veux importer des écritures comptables depuis un fichier Excel | Template de saisie Excel téléchargeable. Colonnes : date, journal, numéro pièce, compte, tiers, libellé, débit, crédit. Processus : upload → parsing → validation → preview (avec erreurs ligne par ligne) → confirmation → import en BROUILLARD. | - Template Excel téléchargeable avec colonnes pré-définies<br>- Validation : comptes existants, équilibre par pièce, format date, NUMERIC<br>- Rapport d'erreurs ligne par ligne (numéro de ligne + erreur)<br>- Preview des écritures valides avant import<br>- Import en BROUILLARD uniquement<br>- Import atomique par pièce (une pièce invalide n'empêche pas les autres) | P1 | 08.2.2 | MVP |
| 09.1.2 | Import FEC (Fichier des Écritures Comptables) | En tant que comptable, je veux importer des écritures au format FEC standard | Parsing du format FEC (tab-separated, colonnes normalisées). Mapping des colonnes FEC vers le modèle EasyAccounting. | - Parsing du format FEC standard<br>- Mapping automatique des colonnes<br>- Validation des montants et de l'équilibre<br>- Import en BROUILLARD | P2 | 09.1.1 | V1 |
| 09.1.3 | Import depuis AtlasCompta | En tant que comptable migrant d'Atlas, je veux importer mes données AtlasCompta | Import du plan de comptes, journaux, écritures, à-nouveaux, immobilisations depuis les fichiers d'export AtlasCompta. | - Import du plan de comptes Atlas<br>- Import des journaux et écritures<br>- Import des à-nouveaux<br>- Rapport de migration détaillé<br>- Validation de l'intégrité post-import | P2 | 09.1.1 | V1 |

---

## Bloc 10 — Modèles d'écritures

### Epic 10.1 : Écritures récurrentes et modèles

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 10.1.1 | Modèles d'écritures | En tant que comptable, je veux enregistrer des modèles d'écritures réutilisables | Table `RecurringEntryModel` : nom, journal, lignes (compte, libellé, débit fixe/variable, crédit fixe/variable). Application : le modèle pré-remplit le formulaire, l'utilisateur ajuste les montants et valide. | - Création d'un modèle à partir d'une écriture existante<br>- Création manuelle d'un modèle<br>- Application du modèle en un clic<br>- Les montants fixes sont pré-remplis, les variables sont à saisir<br>- Le libellé peut contenir des variables (mois, année) | P2 | 08.2.2 | V2 |
| 10.1.2 | Écritures récurrentes automatiques | En tant que comptable, je veux programmer des écritures qui se répètent chaque mois | Planification : fréquence (mensuelle, trimestrielle, annuelle), date de génération, période de validité. Job Celery de génération automatique en BROUILLARD. | - Configuration de la récurrence (fréquence, dates)<br>- Génération automatique via job Celery<br>- Écritures générées en BROUILLARD<br>- Notification à l'utilisateur après génération<br>- Possibilité de suspendre/reprendre la récurrence | P2 | 10.1.1 | V2 |

---

## Bloc 11 — TVA

### Epic 11.1 : Paramétrage TVA marocaine

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 11.1.1 | Configuration des taux TVA | En tant que comptable, je veux que les taux TVA marocains soient pré-configurés | Taux via le moteur de règles : 20%, 14%, 10%, 7%, 0% (exonéré), hors champ. Association compte → taux TVA par défaut. Régime : encaissement ou débit. | - Taux TVA marocains disponibles par défaut<br>- Association d'un taux par défaut à chaque compte<br>- Configuration du régime TVA par société (encaissement/débit)<br>- Les taux sont gérés via le moteur de règles (modifiables sans code) | P0 | 27.1.1, 08.1.1 | MVP |
| 11.1.2 | Régime de TVA par société | En tant que comptable, je veux configurer le régime de TVA de chaque société | Configuration par société : régime (mensuel/trimestriel), mode (encaissement/débit), option pour prorata, assujettissement partiel. | - Sélection du régime (mensuel/trimestriel)<br>- Sélection du mode (encaissement/débit)<br>- Option prorata (oui/non avec coefficient)<br>- Configuration sauvegardée au niveau société | P0 | 03.1.3 | MVP |

### Epic 11.2 : Déclaration de TVA

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 11.2.1 | Calcul automatique de la TVA | En tant que comptable, je veux que la déclaration de TVA soit calculée automatiquement à partir des écritures | Service de calcul : collecte des écritures TVA de la période, regroupement par taux, calcul TVA collectée (ventes) et TVA déductible (achats avec décalage d'un mois), TVA due = collectée - déductible - crédit antérieur. | - Calcul automatique basé sur les écritures validées<br>- Regroupement par taux (20%, 14%, 10%, 7%)<br>- Décalage d'un mois pour la TVA déductible (règle marocaine)<br>- Report automatique du crédit de TVA du mois précédent<br>- TVA due = collectée − déductible − crédit antérieur<br>- Montants arrondis au dirham inférieur | P0 | 08.2.3, 11.1.1 | MVP |
| 11.2.2 | Interface de déclaration TVA | En tant que comptable, je veux visualiser, ajuster et valider ma déclaration de TVA | Écran de déclaration : synthèse par taux, détail des écritures par ligne, possibilité d'ajustement manuel avec justification, validation, génération PDF. | - Synthèse claire par taux avec détail drilldown<br>- Ajustement manuel possible avec saisie de justification obligatoire<br>- Validation avec verrouillage (immuable après validation)<br>- Génération PDF du récapitulatif<br>- Historique des déclarations précédentes | P0 | 11.2.1 | MVP |
| 11.2.3 | Génération XML EDI pour la DGI | En tant que comptable, je veux générer le fichier XML de télédéclaration TVA conforme au format DGI | Génération du fichier XML conforme au XSD de la DGI. Validation du XML contre le XSD avant téléchargement. Le fichier est téléchargé manuellement par l'utilisateur et déposé sur le portail DGI (pas de dépôt automatique en V1). | - Génération XML conforme au XSD DGI<br>- Validation automatique du XML contre le XSD<br>- Téléchargement du fichier XML<br>- Rapport de validation avec erreurs le cas échéant<br>- Pas de dépôt automatique (dépôt manuel par l'utilisateur) | P1 | 11.2.2 | V1 |
| 11.2.4 | Prorata de déduction TVA | En tant que comptable, je veux appliquer le prorata de déduction pour les sociétés à activité mixte | Calcul du prorata provisoire et définitif. Application automatique du coefficient de déduction. Régularisation annuelle. | - Saisie du coefficient provisoire en début d'exercice<br>- Application automatique aux achats<br>- Calcul du prorata définitif en fin d'exercice<br>- Régularisation automatique<br>- Écriture de régularisation générée | P2 | 11.2.1 | V2 |

---

## Bloc 12 — Clôture / Réouverture / À-nouveaux

### Epic 12.1 : Processus de clôture

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 12.1.1 | Contrôles pré-clôture | En tant qu'expert-comptable, je veux lancer des contrôles de cohérence avant de clôturer un exercice | Checklist automatique : toutes les périodes clôturées, toutes les écritures validées, équilibre vérifié, TVA déclarée, immobilisations amorties, comptes d'attente soldés. Rapport avec statut par contrôle (OK / Warning / Bloquant). | - Checklist de contrôles exécutée automatiquement<br>- Statut par contrôle : OK, Warning, Bloquant<br>- Impossible de clôturer si contrôles bloquants<br>- Possibilité de forcer malgré les warnings (avec justification)<br>- Rapport PDF téléchargeable | P0 | 04.1.3, 08.2.3, 11.2.2 | MVP |
| 12.1.2 | Clôture d'exercice | En tant qu'expert-comptable, je veux clôturer un exercice définitivement | Action de clôture : passe l'exercice en CLÔTURÉ, verrouille toutes les écritures, déclenche la génération des à-nouveaux. Irréversible sauf réouverture exceptionnelle. | - L'exercice passe en statut CLÔTURÉ<br>- Toutes les écritures sont verrouillées<br>- Aucune nouvelle écriture possible<br>- Génération automatique des à-nouveaux<br>- Log d'audit avec horodatage et utilisateur<br>- Confirmation en deux étapes (saisie de code de confirmation) | P0 | 12.1.1 | MVP |
| 12.1.3 | Génération des à-nouveaux | En tant que comptable, je veux que les à-nouveaux de l'exercice suivant soient générés automatiquement | Calcul des soldes de chaque compte de bilan (classes 1-5). Génération d'une écriture d'à-nouveau dans le journal AN de l'exercice suivant. Report du résultat de l'exercice au compte 1200 (Résultat de l'exercice). | - Soldes de bilan (classes 1-5) reportés<br>- Écriture d'à-nouveau générée dans le journal AN<br>- Résultat affecté au compte 1200<br>- Lettrage maintenu sur les comptes de tiers<br>- Vérification d'équilibre de l'écriture d'à-nouveau<br>- Report des détails de lettrage pour les tiers non soldés | P0 | 12.1.2 | MVP |
| 12.1.4 | Réouverture exceptionnelle | En tant qu'administrateur, je veux pouvoir réouvrir un exercice clôturé en cas d'erreur grave | Action réservée à l'admin. Passage CLÔTURÉ → RÉOUVERT. Suppression des à-nouveaux générés. Re-génération après correction. Trace d'audit renforcée (motif obligatoire). | - Réouverture réservée au rôle Administrateur<br>- Motif de réouverture obligatoire<br>- Suppression automatique des à-nouveaux existants<br>- L'exercice repasse en statut OUVERT<br>- Trace d'audit renforcée<br>- Notification aux utilisateurs du dossier | P1 | 12.1.2 | MVP |

---

## Bloc 13 — Lettrage

### Epic 13.1 : Lettrage des comptes de tiers

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 13.1.1 | Lettrage manuel | En tant que comptable, je veux lettrer manuellement les écritures d'un compte tiers | Interface de lettrage : affichage des lignes non lettrées d'un compte (par tiers), sélection multiple, vérification d'équilibre, attribution d'un code lettre (A, B, C...). Lettrage partiel possible (écart < seuil paramétrable). | - Affichage des lignes non lettrées d'un compte<br>- Sélection de lignes pour lettrage<br>- Contrôle d'équilibre (débit sélectionné = crédit sélectionné)<br>- Attribution automatique du code lettre<br>- Lettrage partiel avec écart < seuil (paramétrable, défaut 0.10 MAD)<br>- Écriture d'écart automatique si lettrage partiel<br>- Délettrage possible tant que la période est ouverte | P0 | 08.2.2 | MVP |
| 13.1.2 | Lettrage automatique | En tant que comptable, je veux que le système propose un lettrage automatique par correspondance de montants | Algorithme de matching : correspondance exacte montant débit ↔ crédit, correspondance par référence de pièce, correspondance par tiers + montant + date proche. | - Proposition de lettrage par correspondance exacte de montant<br>- Correspondance par numéro de pièce/référence<br>- Proposition soumise à validation humaine<br>- Taux de correspondance affiché<br>- Exécution en lot pour tout un compte | P1 | 13.1.1 | V1 |
| 13.1.3 | Balance âgée | En tant qu'expert-comptable, je veux consulter la balance âgée des tiers pour le suivi des créances et dettes | Rapport de balance âgée : soldes non lettrés par tiers, ventilés par tranche d'ancienneté (0-30j, 31-60j, 61-90j, 91-180j, >180j). | - Balance âgée par tiers<br>- Ventilation par tranche d'ancienneté<br>- Filtres : clients/fournisseurs, date de référence<br>- Export Excel et PDF<br>- Drilldown vers les écritures non lettrées | P1 | 13.1.1 | V1 |

---

## Bloc 14 — Rapprochement bancaire

### Epic 14.1 : Rapprochement bancaire

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 14.1.1 | Import relevé bancaire | En tant que comptable, je veux importer un relevé bancaire depuis un fichier CSV ou Excel | Upload du relevé → parsing → affichage des lignes du relevé avec : date, libellé, référence, montant. Formats supportés : CSV, Excel, OFX. | - Upload de relevé CSV, Excel, OFX<br>- Parsing avec détection automatique des colonnes<br>- Affichage de la liste des mouvements importés<br>- Gestion des doublons (détection par date + montant + référence) | P1 | 08.2.2 | MVP |
| 14.1.2 | Interface de rapprochement | En tant que comptable, je veux rapprocher les écritures comptables avec les mouvements bancaires | Vue en deux colonnes : à gauche les écritures du compte banque, à droite les mouvements du relevé. Rapprochement par glisser-déposer ou sélection multiple. Solde théorique vs solde banque affiché en temps réel. | - Vue double liste (écritures / relevé)<br>- Rapprochement par sélection ou drag & drop<br>- Calcul en temps réel : solde comptable, solde banque, écart<br>- Rapprochement N-N (une écriture peut correspondre à plusieurs lignes de relevé et inversement)<br>- Dé-rapprochement possible tant que la période est ouverte | P1 | 14.1.1 | MVP |
| 14.1.3 | Rapprochement automatique | En tant que comptable, je veux que le système propose des rapprochements automatiques | Matching par : montant exact, montant + date proche (±3 jours), référence/libellé. Propositions soumises à validation. | - Propositions par correspondance exacte de montant<br>- Matching par montant + date proche<br>- Matching par référence<br>- Chaque proposition est validée manuellement<br>- Taux de rapprochement automatique affiché | P2 | 14.1.2 | V1 |
| 14.1.4 | État de rapprochement | En tant que comptable, je veux générer un état de rapprochement bancaire | Rapport : solde du relevé, mouvements non rapprochés (comptables et bancaires), solde comptable ajusté. Format PDF et Excel. | - Génération de l'état de rapprochement<br>- Solde relevé + mouvements non rapprochés banque − mouvements non rapprochés compta = solde comptable<br>- Export PDF et Excel<br>- Historique des rapprochements | P1 | 14.1.2 | V1 |

---

## Bloc 15 — Reporting comptable

### Epic 15.1 : États comptables obligatoires

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 15.1.1 | Balance générale | En tant que comptable, je veux générer la balance générale d'un dossier | Calcul des soldes (débit, crédit, solde) par compte pour une période ou un exercice. Filtres : classe, fourchette de comptes, comptes mouvementés uniquement. | - Balance générale avec débit/crédit/solde par compte<br>- Filtres : période, exercice, classe, fourchette<br>- Option comptes mouvementés uniquement<br>- Totaux par classe<br>- Vérification : total débit = total crédit<br>- Export PDF et Excel | P0 | 08.2.2 | MVP |
| 15.1.2 | Grand livre | En tant que comptable, je veux consulter le grand livre d'un compte | Liste des mouvements d'un compte : date, journal, pièce, libellé, débit, crédit, solde progressif. Filtres : compte, période, tiers. | - Grand livre par compte avec solde progressif<br>- Filtres : période, tiers, journal<br>- Grand livre multi-comptes (fourchette)<br>- Export PDF et Excel<br>- Drill-down vers l'écriture complète | P0 | 08.2.2 | MVP |
| 15.1.3 | Journal centraliseur | En tant que comptable, je veux consulter le journal centraliseur | Totaux débit/crédit par journal et par période. Vue synthétique de l'activité comptable. | - Totaux par journal et par période<br>- Total général<br>- Export PDF et Excel | P0 | 08.2.2 | MVP |
| 15.1.4 | Bilan (actif/passif) | En tant que comptable, je veux générer le bilan comptable conforme au modèle marocain | Bilan format CGNC : Actif (immobilisé + circulant + trésorerie) / Passif (financement permanent + passif circulant + trésorerie passif). Brut, amortissements/provisions, net. Comparatif N-1. | - Format CGNC modèle normal<br>- Actif : brut, amortissements/provisions, net<br>- Passif : montants de l'exercice<br>- Comparatif N-1<br>- Export PDF conforme au modèle officiel | P0 | 08.2.3, 12.1.1 | MVP |
| 15.1.5 | Compte de Produits et Charges (CPC) | En tant que comptable, je veux générer le CPC conforme au modèle marocain | CPC format CGNC : produits d'exploitation, charges d'exploitation, résultat d'exploitation, financier, courant, non courant, résultat avant impôt, résultat net. Comparatif N-1. | - Format CGNC<br>- Structure : exploitation / financier / courant / non courant<br>- Calcul des résultats intermédiaires<br>- Comparatif N-1<br>- Export PDF conforme | P0 | 08.2.3, 12.1.1 | MVP |
| 15.1.6 | État des Soldes de Gestion (ESG) | En tant que comptable, je veux générer l'ESG conforme au modèle marocain | Tableau de formation des résultats (TFR) : marge brute, valeur ajoutée, EBE, résultat d'exploitation, courant, net. Capacité d'autofinancement. | - Format CGNC<br>- Calcul automatique des soldes intermédiaires<br>- Capacité d'autofinancement calculée<br>- Comparatif N-1<br>- Export PDF | P1 | 15.1.5 | V1 |
| 15.1.7 | Tableau de financement | En tant que comptable, je veux générer le tableau de financement marocain | Synthèse des masses du bilan et tableau des emplois/ressources. | - Variation des masses du bilan<br>- Emplois et ressources<br>- Comparatif N-1<br>- Export PDF | P2 | 15.1.4 | V2 |

---

## Bloc 16 — Liasse fiscale / EDI

### Epic 16.1 : Liasse fiscale marocaine

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 16.1.1 | Tableaux de la liasse fiscale | En tant que comptable, je veux générer les tableaux de la liasse fiscale marocaine | Génération automatique des tableaux : bilan actif, bilan passif, CPC, ESG, tableau de financement, état des dérogations, détail des postes du bilan, tableau des provisions, tableau des créances/dettes, répartition du capital. Pré-remplis à partir de la balance. | - Génération de tous les tableaux de la liasse<br>- Pré-remplissage automatique depuis la balance<br>- Possibilité d'ajustement manuel<br>- Format conforme au modèle DGI<br>- Export PDF | P1 | 15.1.4, 15.1.5, 15.1.6 | V1 |
| 16.1.2 | Génération EDI XML liasse | En tant que comptable, je veux générer le fichier EDI XML de la liasse fiscale pour dépôt à la DGI | Génération XML conforme au XSD DGI. Validation automatique. Téléchargement pour dépôt manuel sur simpl.ma. | - XML conforme au XSD DGI<br>- Validation pré-génération<br>- Téléchargement du fichier<br>- Rapport de validation<br>- Archivage automatique du fichier généré | P1 | 16.1.1 | V1 |

---

## Bloc 17 — Paie & RH

### Epic 17.1 : Référentiel paie

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 17.1.1 | Gestion des salariés | En tant que gestionnaire de paie, je veux gérer le fichier du personnel | Table `Employee` : matricule, état civil, CIN, CNSS, CIMR, adresse, RIB, situation familiale, nombre de déductions, date embauche, date sortie. Statuts : actif, en congé, suspendu, sorti. | - CRUD complet des salariés<br>- Champs légaux marocains (CIN, CNSS, CIMR)<br>- Gestion des statuts avec dates<br>- Photo optionnelle<br>- Recherche par matricule, nom, CIN<br>- Import Excel du fichier du personnel | P0 | 03.1.3 | V2 |
| 17.1.2 | Gestion des contrats | En tant que gestionnaire de paie, je veux gérer les contrats de travail | Table `Contract` : type (CDI, CDD, stage, intérim), date début, date fin, salaire de base, mode de paiement, poste, département, coefficient, convention collective. | - CRUD des contrats<br>- Types : CDI, CDD, stage, intérim, ANAPEC<br>- Historique des contrats par salarié<br>- Alertes sur fin de CDD<br>- Un seul contrat actif par salarié à un instant T | P0 | 17.1.1 | V2 |
| 17.1.3 | Rubriques de paie | En tant que gestionnaire de paie, je veux configurer les rubriques de paie | Rubriques par défaut via le moteur de règles : salaire de base, ancienneté, heures supplémentaires, primes, CNSS salariale, AMO, CIMR salariale, IR, avances. Formules de calcul par rubrique. | - Rubriques par défaut créées automatiquement<br>- Formules de calcul configurables<br>- Ordre d'affichage sur le bulletin<br>- Type : gain/retenue/informative<br>- Base de calcul paramétrable | P0 | 27.1.2 | V2 |

### Epic 17.2 : Calcul de paie

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 17.2.1 | Préparation de la paie | En tant que gestionnaire de paie, je veux préparer la paie d'un mois | Ouverture de la période de paie. Saisie des éléments variables : absences, heures supplémentaires, primes, avances, congés. Affichage de la liste des salariés à traiter. | - Ouverture de la période de paie<br>- Saisie des éléments variables par salarié<br>- Import Excel des éléments variables<br>- Liste des salariés avec statut (à traiter / calculé / validé)<br>- Contrôle des éléments saisis | P0 | 17.1.1, 17.1.3 | V2 |
| 17.2.2 | Calcul du bulletin | En tant que gestionnaire de paie, je veux calculer les bulletins de paie | Calcul automatique : salaire brut → cotisations CNSS (plafond 6000 MAD) → AMO (2.26%) → CIMR → salaire net imposable → IR (barème progressif) → salaire net à payer. Via Celery pour calcul en masse. | - Calcul unitaire et en masse (Celery)<br>- CNSS salariale : 4.48% plafonné à 6000 MAD<br>- AMO : 2.26% sans plafond<br>- IR : barème progressif marocain avec déductions familiales<br>- Résultat : brut, net imposable, net à payer<br>- Tous les montants en NUMERIC(15,2)<br>- Traçabilité de chaque étape de calcul | P0 | 17.2.1, 27.1.2 | V2 |
| 17.2.3 | Validation et verrouillage | En tant que responsable paie, je veux valider et verrouiller les bulletins d'un mois | Validation unitaire ou en masse. Bulletin validé = immuable. Génération PDF des bulletins. | - Validation unitaire et en masse<br>- Bulletin validé immuable<br>- Seul le rôle Gestionnaire paie ou Admin peut valider<br>- Log d'audit à la validation | P0 | 17.2.2 | V2 |
| 17.2.4 | Génération des bulletins de paie PDF | En tant que gestionnaire de paie, je veux générer les bulletins de paie au format PDF | Bulletin conforme au modèle marocain : en-tête entreprise/salarié, rubriques avec base/taux/montant, totaux, net à payer. Génération unitaire et en masse. | - Bulletin PDF conforme au format marocain<br>- En-tête : entreprise, salarié, période<br>- Rubriques : code, libellé, base, taux, gain, retenue<br>- Totaux : brut, net imposable, net à payer<br>- Génération en masse via Celery<br>- Stockage dans MinIO | P0 | 17.2.3 | V2 |
| 17.2.5 | Intégration paie → comptabilité | En tant que comptable, je veux que les écritures de paie soient générées automatiquement en comptabilité | Génération automatique de l'écriture de paie dans le journal OD : débit charges de personnel (classe 6), crédit CNSS à payer, IR à payer, nets à payer, etc. Mapping rubrique → compte comptable. | - Écriture de paie générée automatiquement<br>- Mapping rubrique → compte comptable configurable<br>- Écriture en BROUILLARD (validation manuelle par le comptable)<br>- Débit : comptes de charges (61xx)<br>- Crédit : organismes sociaux (44xx), personnel (44xx) | P0 | 17.2.3, 08.2.2 | V2 |

### Epic 17.3 : Gestion des congés et absences

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 17.3.1 | Gestion des congés | En tant que gestionnaire de paie, je veux gérer les demandes de congés | Table `LeaveRequest` : salarié, type (annuel, maladie, maternité, sans solde, exceptionnel), date début, date fin, statut (demandé, approuvé, refusé). Calcul automatique du solde de congés (1.5j/mois au Maroc). | - Saisie des demandes de congés<br>- Types de congés marocains<br>- Calcul automatique du solde (1.5j/mois = 18j/an)<br>- Workflow : demandé → approuvé/refusé<br>- Impact automatique sur la paie (absences) | P1 | 17.1.1 | V2 |
| 17.3.2 | Gestion des prêts salariés | En tant que gestionnaire de paie, je veux gérer les prêts et avances aux salariés | Table `EmployeeLoan` : salarié, montant, mensualité, solde restant, date début. Retenue automatique sur le bulletin. | - Création d'un prêt avec échéancier<br>- Retenue automatique mensuelle sur le bulletin<br>- Solde restant mis à jour<br>- Historique des remboursements | P2 | 17.2.2 | V2 |

---

## Bloc 18 — Déclarations sociales

### Epic 18.1 : Déclarations CNSS et fiscales

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 18.1.1 | Déclaration CNSS mensuelle | En tant que gestionnaire de paie, je veux générer la déclaration CNSS mensuelle | Calcul : cotisations salariales et patronales par salarié. Génération du bordereau CNSS. Cotisations patronales : allocations familiales (6.40%), prestations sociales (8.98%), AMO patronale (4.11%), taxe formation (1.6%). | - Calcul des cotisations salariales et patronales<br>- Bordereau CNSS conforme<br>- Détail par salarié<br>- Totaux par rubrique<br>- Export PDF | P0 | 17.2.3 | V2 |
| 18.1.2 | Fichier DAMANCOM | En tant que gestionnaire de paie, je veux générer le fichier DAMANCOM pour télédéclaration CNSS | Génération du fichier au format DAMANCOM (spécification CNSS). Validation du fichier avant export. | - Format DAMANCOM conforme<br>- Validation pré-génération<br>- Téléchargement du fichier<br>- Rapport de validation | P0 | 18.1.1 | V2 |
| 18.1.3 | État 9421 (IR annuel) | En tant que gestionnaire de paie, je veux générer l'état 9421 de l'IR sur les salaires | Récapitulatif annuel par salarié : brut imposable, frais professionnels, cotisations, net imposable, IR retenu. Format conforme DGI. | - État 9421 conforme au format DGI<br>- Récapitulatif annuel par salarié<br>- Calcul vérifié (somme des bulletins)<br>- Export PDF et XML | P1 | 17.2.3 | V2 |
| 18.1.4 | Régularisation annuelle IR | En tant que gestionnaire de paie, je veux effectuer la régularisation annuelle de l'IR | Recalcul de l'IR sur le cumul annuel. Comparaison avec les retenues mensuelles. Calcul du trop-perçu ou du complément. Intégration sur le bulletin de décembre. | - Recalcul IR annuel vs cumul mensuel<br>- Calcul de l'écart (trop-perçu ou complément)<br>- Application automatique sur le bulletin de décembre<br>- Détail du calcul accessible | P1 | 17.2.2 | V2 |

---

## Bloc 19 — Gestion commerciale

### Epic 19.1 : Cycle commercial

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 19.1.1 | Catalogue produits/services | En tant que commercial, je veux gérer un catalogue de produits et services | Tables `ProductCategory`, `Product`. Produit : code, libellé, catégorie, type (bien/service), prix HT, taux TVA, unité de mesure, code comptable. | - CRUD produits et catégories<br>- Types : bien, service<br>- Prix HT avec taux TVA associé<br>- Compte comptable de vente et d'achat<br>- Gestion des unités de mesure<br>- Import Excel | P0 | 03.1.3 | V3 |
| 19.1.2 | Devis | En tant que commercial, je veux créer des devis pour mes clients | Table `CommercialDocument` (type=DEVIS). En-tête : client, date, validité, objet. Lignes : produit, quantité, prix unitaire, remise, TVA, total. Statuts : BROUILLON → ENVOYÉ → ACCEPTÉ → REFUSÉ → EXPIRÉ. | - Création de devis multi-lignes<br>- Calcul automatique : HT, TVA, TTC<br>- Numérotation automatique (DEV-2026-001)<br>- Conversion en commande/facture<br>- Export PDF avec mise en page professionnelle<br>- Envoi par email (V3+) | P0 | 19.1.1, 08.3.1 | V3 |
| 19.1.3 | Bons de commande | En tant que commercial, je veux convertir un devis en bon de commande | Type=COMMANDE. Conversion depuis devis (pré-remplissage). Statuts : BROUILLON → CONFIRMÉE → LIVRÉE → FACTURÉE. | - Conversion devis → commande en un clic<br>- Modification des quantités/prix possible<br>- Statuts avec workflow<br>- Suivi des commandes en cours | P1 | 19.1.2 | V3 |
| 19.1.4 | Bons de livraison | En tant que commercial, je veux créer des bons de livraison | Type=LIVRAISON. Depuis commande : sélection des lignes livrées, quantité livrée. Impact stock automatique. Livraison partielle possible. | - Création depuis commande<br>- Livraison partielle (suivi du reste à livrer)<br>- Impact stock automatique (déstockage)<br>- Impression du bon de livraison PDF | P1 | 19.1.3, 20.1.2 | V3 |
| 19.1.5 | Facturation | En tant que commercial, je veux créer des factures clients | Type=FACTURE. Depuis devis, commande ou livraison. Calcul TVA automatique. Numérotation séquentielle obligatoire (pas de trou). Facture validée = immuable (avoir obligatoire pour corriger). | - Création de facture depuis devis/commande/livraison<br>- Numérotation séquentielle sans trou (obligation légale)<br>- Calcul TVA automatique par ligne<br>- Facture validée immuable<br>- Mentions légales obligatoires (ICE, IF, RC, TVA)<br>- Export PDF conforme | P0 | 19.1.2 | V3 |
| 19.1.6 | Avoirs | En tant que commercial, je veux émettre des avoirs pour corriger une facture | Type=AVOIR. Référence à la facture d'origine. Montants négatifs. Impact stock (retour) et comptabilité (contrepassation). | - Avoir lié à la facture d'origine<br>- Numérotation séquentielle<br>- Montants négatifs<br>- Retour en stock automatique (si applicable)<br>- Écriture comptable de contrepassation | P0 | 19.1.5 | V3 |
| 19.1.7 | Règlements clients | En tant que commercial, je veux enregistrer les paiements clients | Table `Payment` : client, facture(s), montant, date, mode (chèque, virement, espèces, effet). Règlement partiel possible. Lettrage automatique avec la facture. | - Enregistrement de règlements<br>- Modes : chèque, virement, espèces, effet<br>- Règlement partiel avec solde restant<br>- Lettrage automatique facture ↔ règlement<br>- Écriture comptable générée automatiquement | P0 | 19.1.5, 08.2.2 | V3 |
| 19.1.8 | Intégration commercial → comptabilité | En tant que comptable, je veux que les factures et règlements génèrent automatiquement les écritures comptables | Événement : à la validation d'une facture, génération de l'écriture (débit 3421 client, crédit 71xx produit, crédit 4455 TVA). Au règlement : écriture de trésorerie. | - Écriture de vente générée à la validation de facture<br>- Écriture de règlement générée à l'enregistrement du paiement<br>- Mapping produit → compte comptable<br>- Écritures en BROUILLARD<br>- TVA correctement ventilée par taux | P0 | 19.1.5, 19.1.7, 08.2.2 | V3 |

---

## Bloc 20 — Stock

### Epic 20.1 : Gestion de stock

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 20.1.1 | Dépôts et emplacements | En tant que responsable stock, je veux gérer les dépôts de stockage | Table `Warehouse` : code, libellé, adresse, société. Un dépôt par défaut par société. | - CRUD des dépôts<br>- Un dépôt par défaut par société<br>- Adresse et responsable par dépôt | P1 | 03.1.3 | V3 |
| 20.1.2 | Mouvements de stock | En tant que responsable stock, je veux tracer tous les mouvements de stock | Table `StockMovement` : produit, dépôt, type (entrée/sortie/transfert/inventaire), quantité, coût unitaire, document source. Table `StockLevel` : produit, dépôt, quantité, CMUP. | - Enregistrement automatique des mouvements (livraison, réception, inventaire)<br>- Calcul du CMUP (Coût Moyen Unitaire Pondéré)<br>- Stock en temps réel par produit et par dépôt<br>- Traçabilité complète (lien vers document source) | P0 | 19.1.4 | V3 |
| 20.1.3 | Inventaire physique | En tant que responsable stock, je veux effectuer un inventaire physique | Création d'un inventaire : sélection du dépôt, saisie des quantités physiques, calcul des écarts, validation avec génération des écritures d'ajustement. | - Création d'inventaire par dépôt<br>- Saisie des quantités physiques<br>- Calcul automatique des écarts<br>- Génération des mouvements de régularisation<br>- Écriture comptable d'ajustement (stock → variation de stock) | P1 | 20.1.2 | V3 |
| 20.1.4 | Alertes de stock | En tant que responsable stock, je veux être alerté quand un produit atteint le seuil minimal | Seuil paramétrable par produit. Notification in-app et email quand le stock passe sous le seuil. | - Seuil minimum paramétrable par produit<br>- Alerte in-app quand stock < seuil<br>- Alerte email (si activé)<br>- Tableau de bord des produits en rupture | P2 | 20.1.2, 07.1.1 | V3 |

---

## Bloc 21 — Immobilisations

### Epic 21.1 : Gestion des immobilisations

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 21.1.1 | Fiche immobilisation | En tant que comptable, je veux gérer les immobilisations de l'entreprise | Table `FixedAsset` : code, libellé, catégorie, date acquisition, date mise en service, valeur d'acquisition, durée d'amortissement, méthode (linéaire/dégressif), compte d'immobilisation, compte d'amortissement, compte de dotation. Statuts : EN_SERVICE, CÉDÉE, MISE_AU_REBUT. | - CRUD des immobilisations<br>- Catégories avec durées et taux par défaut (via moteur de règles)<br>- Champs obligatoires : date acquisition, valeur, durée, méthode<br>- Statuts avec dates<br>- Association aux comptes comptables<br>- Import Excel | P0 | 08.1.2, 27.1.3 | MVP |
| 21.1.2 | Plan d'amortissement | En tant que comptable, je veux calculer et consulter le plan d'amortissement d'une immobilisation | Table `DepreciationPlan` : lignes annuelles avec base amortissable, annuité, cumul, VNA. Calcul linéaire (annuité = valeur / durée) et dégressif (coefficient fiscal). Prorata temporis pour l'année d'acquisition. | - Calcul linéaire et dégressif<br>- Prorata temporis (1ère année = jours/360)<br>- Tableau : exercice, base, annuité, cumul, VNA<br>- Recalcul automatique en cas de modification<br>- Export PDF et Excel | P0 | 21.1.1 | MVP |
| 21.1.3 | Dotation aux amortissements | En tant que comptable, je veux passer les écritures de dotation aux amortissements en comptabilité | Génération automatique de l'écriture de dotation : débit compte de dotation (619x), crédit compte d'amortissement (28xx). En lot pour toutes les immobilisations d'un exercice. | - Calcul de la dotation annuelle par immobilisation<br>- Génération de l'écriture en lot<br>- Écriture en BROUILLARD<br>- Vérification que la dotation n'a pas déjà été passée<br>- Détail par immobilisation accessible | P0 | 21.1.2, 08.2.2 | MVP |
| 21.1.4 | Cession et mise au rebut | En tant que comptable, je veux enregistrer la cession ou la mise au rebut d'une immobilisation | Table `AssetDisposal` : date, type (cession/rebut), prix de cession, plus/moins-value calculée. Génération des écritures : sortie de l'actif, annulation de l'amortissement cumulé, constatation de la plus/moins-value. | - Enregistrement de la cession avec prix<br>- Calcul automatique de la plus/moins-value<br>- Prorata temporis pour l'année de cession<br>- Génération des écritures comptables<br>- L'immobilisation passe en statut CÉDÉE/MISE_AU_REBUT | P1 | 21.1.3 | V1 |
| 21.1.5 | État des immobilisations | En tant que comptable, je veux générer le tableau des immobilisations pour la liasse fiscale | État récapitulatif : valeurs brutes (début, acquisitions, cessions, fin), amortissements (début, dotations, reprises, fin), VNA. Par catégorie et par compte. | - Tableau conforme au format de la liasse fiscale<br>- Par catégorie et global<br>- Valeurs d'ouverture et de clôture<br>- Export PDF et Excel | P1 | 21.1.3 | V1 |

---

## Bloc 22 — Analytique

### Epic 22.1 : Comptabilité analytique

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 22.1.1 | Axes et sections analytiques | En tant que contrôleur de gestion, je veux définir des axes et sections analytiques | Tables `AnalyticAxis` (département, projet, région...) et `AnalyticSection` (valeurs de chaque axe). Jusqu'à 5 axes par dossier. | - CRUD des axes et sections<br>- Jusqu'à 5 axes simultanés<br>- Hiérarchie de sections possible (parent/enfant)<br>- Activation/désactivation d'un axe | P1 | 03.1.3 | V2 |
| 22.1.2 | Ventilation analytique sur les écritures | En tant que comptable, je veux ventiler une écriture sur des sections analytiques | Ajout d'un onglet "Analytique" sur le formulaire d'écriture. Ventilation par ligne d'écriture : section, pourcentage ou montant. Total = 100% par ligne. | - Ventilation manuelle par ligne d'écriture<br>- Par pourcentage ou par montant<br>- Contrôle : total ventilé = 100% du montant<br>- Ventilation obligatoire si le compte est analytique (paramétrable)<br>- Ventilation sur plusieurs axes simultanément | P1 | 22.1.1, 08.2.2 | V2 |
| 22.1.3 | Balance et grand livre analytique | En tant que contrôleur de gestion, je veux consulter la balance et le grand livre par axe analytique | Balance : solde par section analytique. Grand livre : mouvements par section. Filtres : axe, section, période, compte. | - Balance analytique par axe/section<br>- Grand livre analytique<br>- Filtres multiples<br>- Comparatif entre sections<br>- Export PDF et Excel | P1 | 22.1.2 | V2 |
| 22.1.4 | Clés de répartition | En tant que contrôleur de gestion, je veux définir des clés de répartition automatiques | Table `AllocationKey` : nom, sections avec pourcentages. Application automatique de la ventilation lors de la saisie d'une écriture sur un compte associé à une clé. | - Définition de clés (sections + %)<br>- Association clé → compte comptable<br>- Ventilation automatique à la saisie<br>- Modification manuelle possible post-ventilation | P2 | 22.1.1 | V4 |

---

## Bloc 23 — Budgets

### Epic 23.1 : Gestion budgétaire

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 23.1.1 | Saisie budgétaire | En tant que contrôleur de gestion, je veux saisir un budget par compte et par période | Tables `Budget`, `BudgetLine`. Budget : exercice, version (initial, révisé), axe analytique (optionnel). Lignes : compte, période, montant. | - Création d'un budget par exercice<br>- Saisie par compte × période (matrice)<br>- Versions : initial, révisé 1, révisé 2...<br>- Copie d'un budget existant comme base<br>- Import Excel | P2 | 04.1.1 | V4 |
| 23.1.2 | Suivi budgétaire | En tant que contrôleur de gestion, je veux comparer le réalisé au budget | Rapport de suivi : par compte et par période, colonnes budget/réalisé/écart/%. Alerte dépassement si écart > seuil. | - Comparaison budget vs réalisé<br>- Écart en valeur et en pourcentage<br>- Alerte si dépassement > seuil paramétrable<br>- Drill-down vers les écritures<br>- Export PDF et Excel | P2 | 23.1.1, 15.1.1 | V4 |

---

## Bloc 24 — Reporting & Dashboards

### Epic 24.1 : Tableaux de bord

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 24.1.1 | Dashboard comptable | En tant que comptable, je veux un tableau de bord synthétique de mon dossier | Widgets : CA du mois, charges du mois, résultat du mois, trésorerie, TVA à déclarer, écritures en brouillard, balance non lettrée. Graphiques : évolution CA/charges sur 12 mois. | - Dashboard par dossier<br>- Widgets avec données en temps réel<br>- Graphique d'évolution mensuelle<br>- Rafraîchissement automatique<br>- Responsive mobile | P1 | 15.1.1 | MVP |
| 24.1.2 | Dashboard multi-dossiers (cabinet) | En tant qu'expert-comptable, je veux un tableau de bord transversal de tous mes dossiers | Vue liste de dossiers avec indicateurs : avancement TVA, avancement clôture, écritures en attente, alertes. Tri et filtres par statut. | - Liste des dossiers avec indicateurs clés<br>- Statut d'avancement par dossier<br>- Alertes (échéances TVA, retards)<br>- Filtres par statut/collaborateur<br>- Export de la vue | P2 | 24.1.1 | V1 |
| 24.1.3 | Dashboard paie | En tant que gestionnaire de paie, je veux un tableau de bord de la masse salariale | Widgets : masse salariale du mois, charges patronales, effectif, variations. Graphiques : évolution masse salariale, répartition par département. | - Données paie synthétiques<br>- Graphiques de tendance<br>- Comparaison M/M-1<br>- Par département/établissement | P2 | 17.2.3 | V2 |
| 24.1.4 | Ratios financiers | En tant que comptable, je veux consulter les principaux ratios financiers | Calcul automatique : fonds de roulement, BFR, trésorerie nette, ratios de liquidité, d'endettement, de rentabilité. | - Calcul automatique des ratios clés<br>- Comparaison N/N-1<br>- Visualisation graphique<br>- Export PDF | P2 | 15.1.4 | V2 |

---

## Bloc 25 — IA documentaire

### Epic 25.1 : OCR et extraction

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 25.1.1 | Service OCR | En tant que développeur, je veux un service d'OCR capable d'extraire le texte de documents scannés | Service Celery wrappant Tesseract ou un service OCR cloud. Input : image ou PDF. Output : texte brut + coordonnées des zones. | - OCR fonctionnel sur PDF et images (JPG, PNG)<br>- Support du français et de l'arabe<br>- Extraction de texte avec coordonnées<br>- Job asynchrone (Celery)<br>- Timeout configurable | P2 | 06.1.1 | V2 |
| 25.1.2 | Extraction structurée de factures | En tant que comptable, je veux que le système extraie automatiquement les données d'une facture | Post-OCR : extraction des champs clés via NLP/regex : fournisseur (nom, ICE), date, numéro de facture, montant HT, TVA, TTC, lignes de détail. Score de confiance par champ. | - Extraction des champs clés<br>- Score de confiance par champ (0-100%)<br>- Champs à faible confiance signalés visuellement<br>- Tous les champs modifiables par l'utilisateur<br>- Apprentissage par fournisseur (amélioration du taux au fil du temps) | P2 | 25.1.1 | V2 |
| 25.1.3 | Saisie assistée par scan | En tant que comptable, je veux scanner une facture et obtenir une écriture pré-remplie | Workflow : upload scan → OCR → extraction → proposition d'écriture (journal, compte, tiers, montants) → validation humaine → écriture en BROUILLARD. | - Upload → OCR → proposition en < 30 secondes<br>- Écriture pré-remplie avec tous les champs<br>- Tiers proposé (par ICE/nom) ou création rapide<br>- Compte comptable suggéré (basé sur l'historique du tiers)<br>- Validation humaine obligatoire<br>- Pièce justificative rattachée automatiquement | P2 | 25.1.2, 08.2.2, 08.3.1 | V2 |

---

## Bloc 26 — IA assistance métier

### Epic 26.1 : Suggestions intelligentes

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 26.1.1 | Suggestion de compte comptable | En tant que comptable, je veux que le système suggère le compte comptable lors de la saisie | Algorithme frequency-based par tiers : mémorise l'association tiers → compte des écritures passées. Suggestion du compte le plus fréquent avec score de confiance. Apprentissage par dossier (isolation). | - Suggestion du compte le plus fréquent pour un tiers donné<br>- Score de confiance affiché<br>- Acceptation en un clic ou saisie manuelle<br>- Apprentissage isolé par dossier<br>- Pas de suggestion si confiance < 60%<br>- Table `AISuggestion` : traçabilité des suggestions et des acceptations | P2 | 08.2.2, 08.3.1 | V2 |
| 26.1.2 | Détection d'anomalies | En tant qu'expert-comptable, je veux être alerté des anomalies potentielles dans les écritures | Détection : doublons (même montant/date/tiers/pièce), montants inhabituels (> 3σ de l'historique du compte), comptes rarement utilisés, écritures à date atypique. Table `AnomalyFlag`. | - Détection de doublons potentiels<br>- Détection de montants inhabituels<br>- Chaque anomalie flaggée avec explication et sévérité<br>- L'utilisateur peut valider (faux positif) ou corriger<br>- Taux de faux positifs < 20%<br>- Dashboard des anomalies | P2 | 08.2.2 | V2 |
| 26.1.3 | Aide au lettrage par IA | En tant que comptable, je veux que l'IA propose des correspondances de lettrage intelligentes | Au-delà du matching simple par montant : matching par pattern de libellé, par fréquence de paiement du tiers, par référence partielle. | - Propositions de lettrage plus intelligentes<br>- Matching par patterns de libellé<br>- Chaque proposition vérifiable par l'utilisateur<br>- Amélioration du taux de lettrage automatique de 20% | P3 | 13.1.2 | V3 |
| 26.1.4 | Classification automatique de documents | En tant que comptable, je veux que les documents uploadés soient classés automatiquement | Classification : facture achat, facture vente, relevé bancaire, bordereau CNSS, avis d'imposition, contrat, autre. Basé sur le contenu OCR. | - Classification automatique avec score de confiance<br>- Catégories prédéfinies<br>- Correction manuelle possible<br>- Apprentissage à partir des corrections | P3 | 25.1.1 | V3 |

---

## Bloc 27 — Moteur de règles

### Epic 27.1 : Moteur de règles métier

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 27.1.1 | Infrastructure du moteur de règles | En tant qu'architecte, je veux un moteur de règles versionné et configurable pour gérer les paramètres réglementaires | Tables `Rule`, `RuleVersion`. Catégories : TVA, IR, CNSS, CIMR, AMORTISSEMENT, PLAN_COMPTABLE, PAIE. Portée : NATIONAL (loi) / ENTERPRISE (paramétrage). Types de valeur : DECIMAL, PERCENTAGE, JSON, TABLE, FORMULA. Versioning avec date d'effet. | - CRUD des règles avec versioning<br>- Date d'effet sur chaque version<br>- La version applicable est celle dont la date d'effet ≤ date de calcul<br>- Portée NATIONAL non modifiable par les tenants<br>- Portée ENTERPRISE modifiable par les admins<br>- Valeurs stockées en JSONB | P0 | 01.1.4 | MVP |
| 27.1.2 | Règles IR et CNSS | En tant qu'architecte, je veux les barèmes IR et taux CNSS configurés dans le moteur de règles | Barème IR 2024 : tranches 0-30k/30k-50k/50k-60k/60k-80k/80k-180k/>180k avec taux 0%/10%/20%/30%/34%/38%. Taux CNSS : salariale (4.48% plafond 6000), patronale (8.98%+6.40%+4.11%+1.6%). Fonctions `compute_ir()` et `compute_cnss()`. | - Barème IR marocain chargé en seed<br>- Taux CNSS chargés en seed<br>- Fonction `compute_ir(net_imposable, deductions)` → montant IR<br>- Fonction `compute_cnss(salaire_brut)` → cotisations salariales et patronales<br>- Résultats identiques aux calculs manuels (tests avec cas réels) | P0 | 27.1.1 | V2 (seed dès MVP) |
| 27.1.3 | Règles d'amortissement | En tant que comptable, je veux que les taux d'amortissement standards soient pré-configurés | Table de correspondance catégorie → durée → taux. Catégories : constructions (20-25 ans), matériel (10 ans), mobilier (10 ans), matériel de transport (5 ans), matériel informatique (5 ans), agencements (10 ans). | - Table d'amortissement chargée en seed<br>- Catégorie → durée et taux par défaut<br>- Utilisé automatiquement à la création d'une immobilisation<br>- Modifiable au niveau ENTERPRISE | P0 | 27.1.1 | MVP |
| 27.1.4 | Interface d'administration des règles | En tant qu'administrateur, je veux consulter et simuler les règles métier | Écran admin : liste des règles par catégorie, historique des versions, valeur courante, simulateur (ex: simuler le calcul IR pour un salaire donné). | - Liste des règles avec filtres par catégorie/portée<br>- Historique des versions avec diff<br>- Simulateur interactif (input → résultat)<br>- Les règles NATIONAL sont en lecture seule<br>- Les règles ENTERPRISE sont modifiables | P2 | 27.1.1 | V1 |
| 27.1.5 | Journalisation des décisions | En tant qu'auditeur, je veux savoir quelle version de quelle règle a été utilisée pour chaque calcul | Table `RuleDecisionLog` : entity_type, entity_id, rule_id, rule_version_id, input (JSONB), output (JSONB), timestamp. Chaque calcul via le moteur de règles est logué. | - Chaque appel au moteur de règles est loggé<br>- Input et output enregistrés<br>- Lien vers la version de règle utilisée<br>- Consultable via l'interface d'audit<br>- Rétention 10 ans | P2 | 27.1.1, 05.1.1 | V1 |

---

## Bloc 28 — Qualité / Tests / Sécurité / Observabilité

### Epic 28.1 : Tests

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 28.1.1 | Suite de tests unitaires | En tant que développeur, je veux une suite de tests unitaires exécutée en CI | Setup pytest avec fixtures, factories (factory_boy), mocking. Couverture cible : 80% des services métier. | - pytest configuré avec couverture<br>- Factories pour chaque modèle<br>- Tests exécutés en < 2 minutes<br>- Couverture > 80% des services métier<br>- CI bloque si couverture < seuil | P0 | 01.1.5 | MVP |
| 28.1.2 | Tests d'intégration base de données | En tant que développeur, je veux des tests d'intégration qui valident les requêtes SQL et le RLS | Tests avec vraie base PostgreSQL (pas de mock). Validation du RLS : un tenant ne voit jamais les données d'un autre. Validation des cascades, contraintes, index. | - Tests contre PostgreSQL réel<br>- Test RLS : cross-tenant retourne 0 résultats<br>- Test des contraintes d'intégrité<br>- Base de test recréée à chaque run<br>- Exécution en < 5 minutes | P0 | 03.1.1 | MVP |
| 28.1.3 | Tests E2E critiques | En tant que QA, je veux des tests E2E sur les parcours critiques | Tests Playwright sur les 5 parcours critiques : login → saisie d'écriture → validation, déclaration TVA, clôture d'exercice, calcul de paie (V2), facturation (V3). | - 5 scénarios E2E implémentés<br>- Exécution en < 10 minutes<br>- Screenshots en cas d'échec<br>- Exécution en CI sur chaque PR vers main | P1 | 01.1.5 | MVP |
| 28.1.4 | Tests non-régression calculs critiques | En tant que développeur, je veux des tests spécifiques pour les calculs financiers | Tests dédiés : équilibre débit/crédit, calcul IR (cas réels avec résultats attendus), calcul CNSS, TVA avec décalage, amortissement linéaire/dégressif, à-nouveaux. | - 10 tests non-régression critiques<br>- Cas réels avec résultats vérifiés manuellement<br>- Exécution en CI, bloquant<br>- Pas de tolérance sur les arrondis (centimes exactes) | P0 | 27.1.2, 11.2.1, 21.1.2 | MVP |

### Epic 28.2 : Sécurité

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 28.2.1 | Protection OWASP Top 10 | En tant qu'architecte sécurité, je veux que l'application soit protégée contre les vulnérabilités OWASP Top 10 | CSRF token, Content Security Policy, rate limiting (100 req/min par IP), validation d'input (Pydantic), protection contre l'injection SQL (SQLAlchemy ORM), XSS (React échappe par défaut), CORS restrictif. | - CSRF protection active<br>- CSP headers configurés<br>- Rate limiting en place<br>- Tous les inputs validés via Pydantic<br>- CORS restrictif (origines whitelist)<br>- Headers de sécurité (X-Frame-Options, HSTS) | P0 | 01.1.1 | MVP |
| 28.2.2 | Scan de sécurité automatisé | En tant qu'architecte, je veux un scan de sécurité automatisé en CI | Intégration de : bandit (Python), npm audit (Node), Trivy (images Docker), OWASP ZAP (basique, en staging). | - bandit en CI sur chaque PR<br>- npm audit en CI<br>- Trivy scan sur les images Docker<br>- Rapport de vulnérabilités<br>- Build bloqué si vulnérabilité critique | P1 | 01.1.5 | MVP |
| 28.2.3 | Chiffrement des données sensibles | En tant qu'architecte, je veux que les données sensibles soient chiffrées | Chiffrement at-rest : PostgreSQL TDE ou application-level pour CIN, RIB, mots de passe. Chiffrement in-transit : TLS 1.2+ obligatoire. | - Mots de passe hashés (argon2)<br>- CIN et RIB chiffrés en base (AES-256-GCM)<br>- TLS 1.2+ obligatoire<br>- Clés de chiffrement dans un vault (ou .env en dev) | P0 | 01.1.1 | MVP |

### Epic 28.3 : Observabilité

| ID | Feature | User Story | Description | Critères d'acceptation | Priorité | Dépendances | Phase |
|----|---------|-----------|-------------|----------------------|----------|-------------|-------|
| 28.3.1 | Logging structuré | En tant que SRE, je veux des logs structurés et centralisés | structlog configuré : JSON format, tenant_id et user_id dans chaque log, niveaux (DEBUG/INFO/WARNING/ERROR/CRITICAL), corrélation par request_id. | - Logs en JSON structuré<br>- tenant_id et user_id dans chaque log<br>- request_id pour corrélation<br>- Niveaux de log respectés<br>- Rotation et rétention configurées | P0 | 01.1.1 | MVP |
| 28.3.2 | Métriques Prometheus | En tant que SRE, je veux des métriques exposées pour le monitoring | Endpoint `/metrics` Prometheus. Métriques : requêtes HTTP (count, latence, erreurs), jobs Celery, connexions DB, taille des queues. | - Endpoint `/metrics` fonctionnel<br>- Métriques HTTP (latence P50/P95/P99)<br>- Métriques Celery (jobs en cours, échoués)<br>- Dashboard Grafana de base | P1 | 01.1.1 | MVP |
| 28.3.3 | Error tracking | En tant que développeur, je veux être alerté des erreurs en production | Intégration Sentry : capture automatique des exceptions, contexte utilisateur/tenant, source maps frontend, alertes par email/Slack. | - Sentry configuré pour backend et frontend<br>- Contexte tenant/user attaché<br>- Source maps uploadées<br>- Alertes sur nouvelles erreurs | P1 | 01.1.1 | MVP |
| 28.3.4 | Healthcheck et readiness | En tant que SRE, je veux des endpoints de vérification de santé | `/api/v1/health` (liveness), `/api/v1/ready` (readiness : vérifie DB, Redis, MinIO). | - `/health` retourne 200 si le service tourne<br>- `/ready` vérifie la connectivité DB, Redis, MinIO<br>- Utilisables par Docker healthcheck et load balancer | P0 | 01.1.1 | MVP |

---

# 3. Roadmap par phases

---

## Phase 0 — MVP (Mois 0–4)

### Objectif

Livrer un socle technique solide et un module comptabilité minimal mais fonctionnel, testable par l'équipe interne et 3-5 cabinets pilotes. Le MVP prouve que la plateforme peut gérer la tenue comptable d'un dossier client avec les standards marocains.

### Modules et blocs concernés

| Bloc | Périmètre MVP | Stories clés |
|------|--------------|-------------|
| 01 - Socle | Infra complète, Docker, CI/CD, bus événements | 01.1.1 → 01.1.6, 01.2.1 |
| 02 - Auth/RBAC | Login, JWT, MFA, RBAC avec 6 rôles | 02.1.1 → 02.1.4, 02.2.1, 02.2.2, 02.2.4 |
| 03 - Multi-tenant | RLS, tenants, sociétés, dossiers, context switcher | 03.1.1 → 03.1.4 |
| 04 - Exercices | Exercices, périodes, verrouillage | 04.1.1 → 04.1.3 |
| 05 - Audit | Audit log immutable | 05.1.1, 05.1.2 |
| 06 - Documents | Upload/stockage MinIO, rattachement pièces | 06.1.1, 06.1.2 |
| 07 - Notifications | Notifications in-app basiques | 07.1.1 |
| 08 - Comptabilité | PCM CGNC, journaux, écritures, validation, contrepassation, tiers | 08.1.1 → 08.3.2 |
| 09 - Imports | Import Excel d'écritures | 09.1.1 |
| 11 - TVA | Taux TVA, calcul déclaration, interface | 11.1.1, 11.1.2, 11.2.1, 11.2.2 |
| 12 - Clôture | Contrôles, clôture, à-nouveaux, réouverture | 12.1.1 → 12.1.4 |
| 13 - Lettrage | Lettrage manuel | 13.1.1 |
| 14 - Rapprochement | Import relevé, interface rapprochement | 14.1.1, 14.1.2 |
| 15 - Reporting | Balance, grand livre, journal, bilan, CPC | 15.1.1 → 15.1.5 |
| 21 - Immobilisations | Fiche, plan d'amortissement, dotation | 21.1.1 → 21.1.3 |
| 24 - Dashboards | Dashboard comptable basique | 24.1.1 |
| 27 - Moteur de règles | Infrastructure, taux TVA, plan comptable, amortissements | 27.1.1, 27.1.3 |
| 28 - Qualité | Tests unitaires, intégration, sécurité OWASP, logging, healthcheck | 28.1.1 → 28.1.4, 28.2.1, 28.2.3, 28.3.1, 28.3.4 |

### Sprints indicatifs (2 semaines)

| Sprint | Focus | Livrables |
|--------|-------|-----------|
| S0 (Sem 1-2) | Architecture | Scaffolding backend + frontend, Docker, CI/CD, Alembic, design system |
| S1 (Sem 3-4) | Socle auth | RLS, auth JWT, MFA, RBAC, middleware, modèle tenant/société/dossier |
| S2 (Sem 5-6) | Socle métier | Exercices, périodes, plan de comptes CGNC, moteur de règles (infra + TVA + amortissements) |
| S3 (Sem 7-8) | Comptabilité cœur | Journaux, saisie d'écritures, validation, contrepassation, tiers, audit log |
| S4 (Sem 9-10) | Compta étendue | Lettrage manuel, import relevé bancaire, rapprochement bancaire, import Excel |
| S5 (Sem 11-12) | TVA + Immos | Déclaration TVA (calcul + interface), immobilisations (fiche + plan + dotation) |
| S6 (Sem 13-14) | Reporting | Balance, grand livre, journal centraliseur, bilan, CPC, dashboard |
| S7 (Sem 15-16) | Clôture + Polish | Clôture/à-nouveaux, documents (upload + pièces jointes), notifications, tests E2E, stabilisation |

### Dépendances critiques

```
RLS (03.1.1) ──→ Tous les modules
Auth (02.1.1) ──→ Tous les endpoints
Exercices (04.1.1) ──→ Écritures, TVA, Clôture
Plan de comptes (08.1.1) ──→ Écritures, TVA, Reporting, Immobilisations
Moteur de règles (27.1.1) ──→ Taux TVA, Plan comptable, Amortissements
Écritures validées (08.2.3) ──→ TVA, Clôture, Reporting
```

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Complexité du RLS PostgreSQL sous-estimée | Moyenne | Élevé | POC en sprint 0, tests d'isolation dès S1 |
| Plan de comptes CGNC incomplet ou incorrect | Faible | Élevé | Validation par expert-comptable certifié |
| Performance de la balance/bilan sur gros volumes | Moyenne | Moyen | Index dès le départ, tests de charge en S7 |
| Périmètre MVP trop large, glissement | Élevée | Élevé | Revue de scope hebdomadaire, priorisation stricte |

### Critères de sortie MVP

- [ ] Un utilisateur peut s'inscrire, créer un dossier et saisir des écritures
- [ ] Le plan de comptes CGNC est initialisé automatiquement
- [ ] Les écritures peuvent être validées (immutables) et contrepassées
- [ ] Le lettrage manuel fonctionne
- [ ] La balance, le grand livre, le bilan et le CPC sont générés correctement
- [ ] La déclaration de TVA est calculée avec le décalage d'un mois
- [ ] Les immobilisations sont gérées avec plan d'amortissement et dotation
- [ ] La clôture d'exercice génère les à-nouveaux
- [ ] L'audit log trace toutes les actions
- [ ] Le RLS empêche tout accès cross-tenant
- [ ] Les tests passent en CI avec couverture > 80% des services
- [ ] 3 cabinets pilotes peuvent l'utiliser pour un dossier de test

---

## Phase 1 — V1 Exploitable (Mois 4–9)

### Objectif

Transformer le MVP en produit exploitable en production par des cabinets comptables. Ajouter les fonctionnalités manquantes pour la conformité complète (liasse fiscale, EDI XML), les workflows avancés (lettrage automatique, rapprochement automatique), et l'ergonomie (rôles personnalisés, historique d'entité, exports avancés).

### Modules et blocs concernés

| Bloc | Périmètre V1 | Stories clés |
|------|--------------|-------------|
| 01 - Socle | Paramétrage interface | 01.2.2 |
| 02 - Auth/RBAC | Rôles personnalisés | 02.2.3 |
| 05 - Audit | Historique d'entité | 05.1.3 |
| 06 - Documents | Explorateur de documents | 06.1.3 |
| 09 - Imports | Import FEC, import AtlasCompta | 09.1.2, 09.1.3 |
| 11 - TVA | Génération EDI XML TVA | 11.2.3 |
| 13 - Lettrage | Lettrage automatique, balance âgée | 13.1.2, 13.1.3 |
| 14 - Rapprochement | Rapprochement auto, état de rapprochement | 14.1.3, 14.1.4 |
| 15 - Reporting | ESG | 15.1.6 |
| 16 - Liasse fiscale | Tableaux liasse, EDI XML liasse | 16.1.1, 16.1.2 |
| 21 - Immobilisations | Cession/rebut, état des immobilisations | 21.1.4, 21.1.5 |
| 24 - Dashboards | Dashboard multi-dossiers | 24.1.2 |
| 27 - Moteur de règles | Interface admin, journalisation | 27.1.4, 27.1.5 |
| 28 - Qualité | Scan de sécurité, métriques, Sentry | 28.2.2, 28.3.2, 28.3.3 |

### Dépendances critiques

```
MVP livré et stable ──→ Tout V1
Écritures + balance ──→ Liasse fiscale
Plan d'amortissement ──→ État des immobilisations
Audit log ──→ Journalisation des décisions du moteur de règles
```

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| XSD DGI non disponible ou ambigu | Moyenne | Élevé | Contact DGI anticipé, reverse-engineering des fichiers Atlas |
| Import AtlasCompta : formats non documentés | Élevée | Moyen | Analyse de fichiers réels d'export, support best-effort |
| Retours pilotes MVP nécessitant refactoring | Moyenne | Moyen | Allocation de 20% de bande passante pour le feedback |

### Critères de sortie V1

- [ ] Un cabinet peut gérer 50+ dossiers en production
- [ ] La liasse fiscale est générée et exportable en EDI XML
- [ ] L'état de rapprochement bancaire est fonctionnel
- [ ] La balance âgée est disponible
- [ ] L'import depuis AtlasCompta est fonctionnel
- [ ] Le dashboard multi-dossiers permet un suivi transversal
- [ ] Le moteur de règles a une interface d'administration
- [ ] < 5 bugs critiques ouverts
- [ ] Temps de réponse moyen < 500ms sur les endpoints principaux

---

## Phase 2 — V2 : Paie + IA de base (Mois 9–15)

### Objectif

Ajouter le module paie marocaine complète avec intégration comptable, les premières fonctions IA (OCR, suggestions), et les briques analytiques de base. C'est la version qui transforme EasyAccounting d'un logiciel de comptabilité en un vrai ERP pour fiduciaires et PME.

### Modules et blocs concernés

| Bloc | Périmètre V2 | Stories clés |
|------|--------------|-------------|
| 03 - Structure | Établissements | 03.1.5 |
| 07 - Notifications | Email, workflow | 07.1.2, 07.1.3 |
| 10 - Modèles | Modèles d'écritures, récurrentes | 10.1.1, 10.1.2 |
| 11 - TVA | Prorata de déduction | 11.2.4 |
| 15 - Reporting | Tableau de financement | 15.1.7 |
| 17 - Paie | Salariés, contrats, rubriques, calcul, validation, bulletins PDF, intégration compta | 17.1.1 → 17.3.2 |
| 18 - Déclarations | CNSS, DAMANCOM, état 9421, régularisation IR | 18.1.1 → 18.1.4 |
| 22 - Analytique | Axes, sections, ventilation, balance analytique | 22.1.1 → 22.1.3 |
| 24 - Dashboards | Dashboard paie, ratios financiers | 24.1.3, 24.1.4 |
| 25 - IA documentaire | OCR, extraction factures, saisie assistée | 25.1.1 → 25.1.3 |
| 26 - IA métier | Suggestions compte, détection anomalies | 26.1.1, 26.1.2 |
| 27 - Moteur de règles | Barèmes IR, taux CNSS | 27.1.2 |

### Dépendances critiques

```
V1 stable ──→ Tout V2
Moteur de règles + barèmes IR/CNSS (27.1.2) ──→ Calcul paie (17.2.2)
Calcul paie (17.2.2) ──→ Bulletins, déclarations, intégration compta
Salariés + contrats (17.1) ──→ Calcul paie
OCR (25.1.1) ──→ Extraction (25.1.2) ──→ Saisie assistée (25.1.3)
Écritures historiques ──→ Suggestion de compte (26.1.1)
Établissements (03.1.5) ──→ CNSS par établissement
```

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Calcul de paie incorrect (IR, CNSS) | Moyenne | Critique | Validation par cabinet d'expertise, tests avec cas réels fournis par les pilotes |
| Format DAMANCOM non conforme | Moyenne | Élevé | Reverse-engineering de fichiers DAMANCOM générés par Atlas |
| OCR peu performant sur factures marocaines (arabe + français) | Élevée | Moyen | Support arabe en V3, focus français en V2, fallback sur saisie manuelle |
| Complexité paie sous-estimée (cas particuliers : départ, rappel, régularisation) | Élevée | Élevé | Périmètre V2 = CDI classique, cas complexes en V3 |

### Critères de sortie V2

- [ ] Un gestionnaire de paie peut calculer et valider les bulletins d'un mois
- [ ] Les bulletins de paie PDF sont conformes au format marocain
- [ ] L'écriture de paie est générée automatiquement en comptabilité
- [ ] Le fichier DAMANCOM est généré et valide
- [ ] L'état 9421 est conforme
- [ ] L'OCR extrait les champs clés d'une facture standard avec > 80% de précision
- [ ] La suggestion de compte fonctionne avec > 70% de pertinence après 50 écritures
- [ ] La balance analytique est fonctionnelle
- [ ] Le calcul IR et CNSS est certifié exact sur 100 cas de test

---

## Phase 3 — V3 : Commercial + Stock (Mois 15–21)

### Objectif

Ajouter le cycle commercial complet (devis → commande → livraison → facture → règlement) avec gestion de stock et intégration comptable automatique. C'est la version qui étend EasyAccounting aux PME commerciales et industrielles.

### Modules et blocs concernés

| Bloc | Périmètre V3 | Stories clés |
|------|--------------|-------------|
| 02 - Auth | SSO SAML/OIDC | 02.1.5 |
| 19 - Commercial | Catalogue, devis, commandes, livraisons, factures, avoirs, règlements, intégration compta | 19.1.1 → 19.1.8 |
| 20 - Stock | Dépôts, mouvements, inventaire, alertes | 20.1.1 → 20.1.4 |
| 26 - IA métier | Aide lettrage IA, classification documents | 26.1.3, 26.1.4 |

### Dépendances critiques

```
V2 stable ──→ Tout V3
Tiers (08.3.1) ──→ Clients/fournisseurs commerciaux
Plan de comptes (08.1.1) ──→ Mapping produit → compte
Écritures (08.2.2) ──→ Intégration commercial → compta
Stock (20.1.2) ──→ Livraisons, inventaire
```

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Numérotation séquentielle de factures (obligation légale) complexe en multi-utilisateur | Moyenne | Élevé | Séquence PostgreSQL par société, verrouillage optimiste |
| Performance stock temps réel sur gros volumes | Faible | Moyen | Vue matérialisée `StockLevel`, index composites |
| Scope commercial trop large (cycle achat complet) | Élevée | Moyen | V3 = vente uniquement, achats en V3+ |

### Critères de sortie V3

- [ ] Le cycle devis → commande → livraison → facture → règlement est fonctionnel
- [ ] Les factures génèrent automatiquement les écritures comptables
- [ ] La numérotation des factures est séquentielle sans trou
- [ ] Le stock est mis à jour en temps réel aux mouvements
- [ ] L'inventaire physique fonctionne avec régularisation comptable
- [ ] Le SSO SAML/OIDC est fonctionnel pour les entreprises

---

## Phase 4 — V4 : Analytique avancé + IA mature (Mois 21–27)

### Objectif

Compléter la plateforme avec les fonctions de pilotage financier avancé (budgets, consolidation), les portails collaboratifs (client, salarié) et les fonctions IA matures. C'est la version qui positionne EasyAccounting comme LA plateforme de gestion intégrée de référence au Maroc.

### Modules et blocs concernés

| Bloc | Périmètre V4 | Stories clés |
|------|--------------|-------------|
| 22 - Analytique | Clés de répartition | 22.1.4 |
| 23 - Budgets | Saisie budgétaire, suivi budgétaire | 23.1.1, 23.1.2 |
| Portails | Portail client, portail salarié | (nouvelles stories) |
| IA avancée | Chatbot, prédiction, consolidation | (nouvelles stories) |
| Consolidation | Reporting consolidé multi-sociétés | (nouvelles stories) |

### Dépendances critiques

```
V3 stable ──→ Tout V4
Analytique (22.1) ──→ Budgets (23.1)
Tous les modules ──→ Consolidation
Paie (17) ──→ Portail salarié
```

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Consolidation multi-sociétés très complexe | Élevée | Moyen | Périmètre V4 = consolidation simplifiée (somme des balances), pas de consolidation IFRS |
| IA chatbot : expectations vs réalité | Élevée | Moyen | Cadrer les cas d'usage stricts, pas de promesse de chatbot généraliste |
| Portail client : sécurité et isolation | Moyenne | Élevé | Audit de sécurité dédié, permissions ultra-restrictives |

### Critères de sortie V4

- [ ] Les budgets sont saisissables avec suivi vs réalisé
- [ ] Les clés de répartition analytique fonctionnent
- [ ] Le reporting consolidé multi-sociétés est disponible
- [ ] Les portails client et salarié sont fonctionnels et sécurisés

---

# 4. Matrice des dépendances inter-blocs

```
Légende : A ──→ B signifie "A est un prérequis de B"

01 Socle ──→ Tous les blocs

02 Auth/RBAC ──→ Tous les blocs (protection des endpoints)

03 Multi-tenant ──→ Tous les blocs (isolation des données)
   03 ──→ 04 (exercices scopés par dossier)
   03 ──→ 08 (comptabilité scopée par dossier)

04 Exercices ──→ 08 (écritures dans un exercice/période)
   04 ──→ 11 (TVA par période)
   04 ──→ 12 (clôture d'un exercice)
   04 ──→ 15 (reporting par exercice)
   04 ──→ 21 (amortissements par exercice)

05 Audit ──→ Aucun prérequis technique, mais consomme les événements de tous les blocs

06 Documents ──→ 25 (OCR sur documents)
   08 ──→ 06 (rattachement pièces aux écritures)

07 Notifications ──→ Consomme les événements de tous les blocs

08 Comptabilité ──→ 11 (TVA calculée sur les écritures)
   08 ──→ 12 (clôture = verrouillage des écritures)
   08 ──→ 13 (lettrage des lignes d'écriture)
   08 ──→ 14 (rapprochement = matching écritures/relevé)
   08 ──→ 15 (reporting = agrégation des écritures)

09 Imports ──→ 08 (import dans le module comptabilité)

10 Modèles ──→ 08 (modèles de saisie d'écritures)

11 TVA ──→ 08 (écritures avec TVA)
   11 ──→ 27 (taux via moteur de règles)

12 Clôture ──→ 04 (exercice à clôturer)
   12 ──→ 08 (écritures à verrouiller)
   12 ──→ 11 (TVA déclarée avant clôture)
   12 ──→ 21 (amortissements passés avant clôture)

13 Lettrage ──→ 08 (lignes d'écriture)

14 Rapprochement ──→ 08 (écritures banque)

15 Reporting ──→ 08 (données comptables)

16 Liasse fiscale ──→ 15 (états comptables)

17 Paie ──→ 03 (salariés par société)
   17 ──→ 27 (barèmes IR/CNSS)
   17 ──→ 08 (intégration paie → compta)

18 Déclarations sociales ──→ 17 (données paie)

19 Commercial ──→ 08 (intégration factures → compta)
   19 ──→ 20 (livraisons impactent le stock)

20 Stock ──→ 19 (mouvements liés aux livraisons)

21 Immobilisations ──→ 08 (écritures d'amortissement)
   21 ──→ 27 (taux d'amortissement)

22 Analytique ──→ 08 (ventilation des écritures)

23 Budgets ──→ 04 (budget par exercice)
   23 ──→ 22 (budget par axe analytique)
   23 ──→ 15 (comparaison budget vs réalisé)

24 Dashboards ──→ 08, 15, 17, 19, 20 (agrégation de données)

25 IA documentaire ──→ 06 (documents à analyser)

26 IA métier ──→ 08 (historique d'écritures pour l'apprentissage)

27 Moteur de règles ──→ 01 (infrastructure de base)
   27 est consommé par ──→ 11, 17, 21

28 Qualité ──→ En parallèle de tous les blocs
```

---

# 5. Arbitrages MVP

## 5.1 Résumé des arbitrages clés

| # | Arbitrage | Décision | Justification |
|---|-----------|----------|---------------|
| 1 | Comptabilité avant paie | OUI — compta en MVP, paie en V2 | La compta est le socle. Un logiciel de paie sans compta est un silo. Un logiciel de compta sans paie est déjà utile. |
| 2 | TVA dans le MVP | OUI | La déclaration TVA est l'obligation la plus fréquente (mensuelle/trimestrielle). Un comptable ne peut pas travailler sans. |
| 3 | Immobilisations dans le MVP | OUI — immobilisations basiques (fiche + plan + dotation) | Les immobilisations impactent le bilan, le CPC et la liasse. Les cessions peuvent attendre V1. |
| 4 | Reporting (bilan/CPC) dans le MVP | OUI | Un comptable qui ne peut pas générer de bilan ne peut pas utiliser le logiciel. C'est la raison d'être du produit. |
| 5 | Liasse fiscale dans le MVP | NON — V1 | La liasse est annuelle. Le MVP peut survivre sans pendant quelques mois. Mais elle doit être dans V1 impérativement. |
| 6 | IA dans le MVP | NON — V2 | L'IA est un accélérateur, pas un prérequis. Le produit doit fonctionner entièrement en mode manuel. |
| 7 | Moteur de règles dans le MVP | OUI — infrastructure + taux TVA + amortissements | Les paramètres réglementaires doivent être des données dès le jour 1. Pas question de hardcoder les taux TVA. |
| 8 | Lettrage auto dans le MVP | NON — lettrage manuel en MVP, auto en V1 | Le lettrage manuel suffit pour démarrer. L'automatisation est un confort significatif mais pas bloquant. |
| 9 | Rapprochement auto dans le MVP | NON — rapprochement manuel en MVP, auto en V1 | Même logique que le lettrage. |
| 10 | Multi-devises dans le MVP | NON — V2 | Le MAD suffit pour 95% des dossiers marocains. Les devises étrangères ajoutent une complexité disproportionnée. |
| 11 | Email notifications dans le MVP | NON — in-app seulement en MVP | Les notifications in-app suffisent pour le MVP. L'email ajoute de la complexité (SMTP, templates, deliverability). |
| 12 | Écritures récurrentes dans le MVP | NON — V2 | La saisie manuelle et l'import Excel suffisent pour le MVP. |

## 5.2 Taille estimée du backlog

| Phase | Epics | Features | User Stories | Estimation relative |
|-------|-------|----------|-------------|-------------------|
| MVP | 15 | 42 | ~80 | Base |
| V1 | 8 | 18 | ~35 | +40% |
| V2 | 12 | 38 | ~70 | +85% |
| V3 | 5 | 16 | ~30 | +35% |
| V4 | 4 | 8 | ~15 | +20% |
| **Total** | **44** | **122** | **~230** | — |

## 5.3 Ce qui rend le produit réellement usable

Le seuil d'usabilité réelle (un cabinet peut migrer un dossier client) est atteint quand **toutes** ces conditions sont remplies :

1. **Saisie d'écritures** avec validation et contrepassation ✓ MVP
2. **Plan de comptes CGNC** initialisé ✓ MVP
3. **Balance et grand livre** corrects ✓ MVP
4. **Bilan et CPC** conformes au modèle marocain ✓ MVP
5. **Déclaration de TVA** avec décalage d'un mois ✓ MVP
6. **Immobilisations** avec plan d'amortissement ✓ MVP
7. **Clôture d'exercice** avec à-nouveaux ✓ MVP
8. **Import de données** depuis l'ancien outil ✓ MVP (Excel) / V1 (Atlas)
9. **Lettrage** des comptes de tiers ✓ MVP (manuel)
10. **Audit trail** pour la conformité ✓ MVP

Le **MVP atteint ce seuil** pour les fonctions de base. La **V1** complète le tableau avec la liasse fiscale et les imports Atlas, ce qui rend la **migration réelle possible** depuis les outils existants.

---

*Fin du document — Backlog Produit & Roadmap EasyAccounting v1.0*
