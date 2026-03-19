# EASYACCOUNTING — Architecture Technique Complète

## ERP SaaS marocain unifié — Software Architecture Document

**Version** : 1.0
**Date** : 18 mars 2026
**Statut** : Draft initial
**Références** : PRD v1.0, Architecture Fonctionnelle v1.0
**Classification** : Confidentiel — Usage interne

---

## Table des matières

1. [Vision architecture globale](#1-vision-architecture-globale)
2. [Choix techniques justifiés](#2-choix-techniques-justifiés)
3. [Architecture backend détaillée](#3-architecture-backend-détaillée)
4. [Architecture frontend détaillée](#4-architecture-frontend-détaillée)
5. [Architecture API](#5-architecture-api)
6. [Architecture sécurité / auth / RBAC](#6-architecture-sécurité--auth--rbac)
7. [Architecture multi-tenant](#7-architecture-multi-tenant)
8. [Architecture documentaire](#8-architecture-documentaire)
9. [Architecture des notifications](#9-architecture-des-notifications)
10. [Architecture reporting / exports](#10-architecture-reporting--exports)
11. [Architecture IA](#11-architecture-ia)
12. [Architecture du moteur de règles](#12-architecture-du-moteur-de-règles)
13. [Modèle de données de haut niveau](#13-modèle-de-données-de-haut-niveau)
14. [Relations principales entre entités](#14-relations-principales-entre-entités)
15. [Stratégie migrations / versioning](#15-stratégie-migrations--versioning)
16. [Stratégie audit log](#16-stratégie-audit-log)
17. [Stratégie tests](#17-stratégie-tests)
18. [Stratégie observabilité / logs](#18-stratégie-observabilité--logs)
19. [Stratégie jobs async](#19-stratégie-jobs-async)
20. [Risques techniques majeurs](#20-risques-techniques-majeurs)

---

# 1. Vision architecture globale

## 1.1 Principes directeurs

| Principe | Implication technique |
|----------|----------------------|
| **Modular monolith first** | On ne commence PAS par des microservices. On structure un monolithe modulaire avec des frontières claires entre domaines. L'extraction en services interviendra si la charge l'exige. |
| **API-first** | Le frontend consomme exactement la même API REST que les intégrations tierces. Aucune logique métier dans le frontend. |
| **Multi-tenant par défaut** | Chaque requête, chaque query, chaque fichier est scopé par `tenant_id`. L'isolation est garantie au niveau de la base de données (Row-Level Security). |
| **Event-driven interne** | Les modules communiquent via un bus d'événements interne (in-process pour le monolithe, migratable vers RabbitMQ/Kafka si extraction). |
| **Convention over configuration** | Conventions strictes de nommage, structure de modules, patterns de code. |
| **Immutabilité comptable** | Les écritures validées et les bulletins validés sont immuables. Pas d'UPDATE, pas de DELETE. |
| **Moteur de règles externalisé** | Les paramètres réglementaires (barème IR, taux CNSS, taux TVA) sont des données, pas du code. |

## 1.2 Vue macro de l'architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                      │
│                                                                           │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│   │  Next.js    │    │  PWA Mobile │    │  API Clients│                 │
│   │  SPA/SSR    │    │  (même app) │    │  (REST)     │                 │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │
└──────────┼──────────────────┼──────────────────┼────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         REVERSE PROXY (Nginx/Caddy)                       │
│                    TLS termination, rate limiting, CORS                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                     FASTAPI APPLICATION                              │ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────┐    │ │
│  │  │                   MIDDLEWARE LAYER                            │   │ │
│  │  │  Auth JWT │ Tenant Context │ RBAC │ Rate Limit │ Audit Log  │   │ │
│  │  └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────┐    │ │
│  │  │                   API ROUTERS (versioned /api/v1/*)          │   │ │
│  │  │  auth│compta│tva│paie│commercial│immo│analytics│reports│...  │   │ │
│  │  └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────┐    │ │
│  │  │                   SERVICE LAYER (Business Logic)             │   │ │
│  │  │                                                               │   │ │
│  │  │  ┌─────────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌──────┐    │   │ │
│  │  │  │ Compta  │ │ TVA │ │Paie │ │ Com │ │Immo │ │Report│    │   │ │
│  │  │  │ Service │ │ Svc │ │ Svc │ │ Svc │ │ Svc │ │ Svc  │    │   │ │
│  │  │  └────┬────┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬───┘    │   │ │
│  │  │       │         │       │       │       │       │          │   │ │
│  │  │  ┌────▼─────────▼───────▼───────▼───────▼───────▼────┐    │   │ │
│  │  │  │             SHARED SERVICES                         │    │   │ │
│  │  │  │  RuleEngine │ EventBus │ AI │ GED │ Audit │ Notif  │    │   │ │
│  │  │  └─────────────────────────────────────────────────────┘    │   │ │
│  │  └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────┐    │ │
│  │  │                   DATA ACCESS LAYER                          │   │ │
│  │  │        SQLAlchemy 2.x + Repository Pattern                   │   │ │
│  │  │        Row-Level Security (tenant_id)                        │   │ │
│  │  └─────────────────────────────────────────────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
├──────────────────────────────────────────────────────────────────────────┤
│                         DATA STORES                                       │
│                                                                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐        │
│  │PostgreSQL │  │   Redis   │  │   MinIO   │  │ Celery/Redis  │        │
│  │ (primary) │  │  (cache)  │  │  (files)  │  │  (job queue)  │        │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────┘        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## 1.3 Structure du monolithe modulaire

```
backend/
├── alembic/                          # Migrations DB
│   ├── versions/
│   └── env.py
├── app/
│   ├── main.py                       # FastAPI app factory
│   ├── config.py                     # Settings from .env
│   ├── database.py                   # SQLAlchemy engine, session
│   │
│   ├── core/                         # Socle transverse
│   │   ├── auth/                     # JWT, MFA, sessions
│   │   ├── tenancy/                  # Middleware multi-tenant, RLS
│   │   ├── rbac/                     # Permissions, policies
│   │   ├── events/                   # Event bus interne
│   │   ├── audit/                    # Audit trail service
│   │   ├── notifications/            # Notification service
│   │   ├── documents/                # GED service
│   │   ├── rules_engine/             # Moteur de règles
│   │   ├── ai/                       # IA service
│   │   ├── export/                   # PDF, Excel generators
│   │   └── exceptions.py             # Exception hierarchy
│   │
│   ├── modules/                      # Modules métier
│   │   ├── accounting/               # Comptabilité
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # API endpoints
│   │   │   ├── service.py            # Business logic
│   │   │   ├── repository.py         # Data access
│   │   │   ├── models.py             # SQLAlchemy models
│   │   │   ├── schemas.py            # Pydantic schemas
│   │   │   ├── events.py             # Domain events
│   │   │   ├── rules.py              # Module-specific rules
│   │   │   └── tests/
│   │   │       ├── test_service.py
│   │   │       ├── test_repository.py
│   │   │       └── test_api.py
│   │   │
│   │   ├── tva/                      # TVA & Fiscalité
│   │   ├── closing/                  # Clôture / À-nouveaux
│   │   ├── payroll/                  # Paie
│   │   ├── commercial/               # Gestion commerciale
│   │   ├── assets/                   # Immobilisations
│   │   ├── analytics/                # Analytique
│   │   ├── budgets/                  # Budgets
│   │   └── reporting/                # Reporting
│   │
│   └── shared/                       # Utilitaires partagés
│       ├── models.py                 # Base models (TenantMixin, AuditMixin)
│       ├── schemas.py                # Shared Pydantic schemas
│       ├── pagination.py             # Pagination helpers
│       ├── filters.py                # Filtering helpers
│       └── decimal_utils.py          # Decimal precision utilities
│
├── tests/                            # Tests d'intégration globaux
├── scripts/                          # Scripts utilitaires
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 2. Choix techniques justifiés

## 2.1 Backend

| Choix | Justification |
|-------|---------------|
| **Python 3.12+** | Écosystème riche pour la comptabilité (décimal natif), la data science (IA), et le recrutement au Maroc. Type hints avancés. |
| **FastAPI** | Performance (ASGI/uvicorn), validation native Pydantic, OpenAPI auto-générée, async natif, dependency injection. |
| **SQLAlchemy 2.x** | ORM mature, support PostgreSQL avancé (JSONB, RLS, partitioning), mode async, type-safe avec `Mapped`. |
| **Alembic** | Standard de fait pour les migrations PostgreSQL avec SQLAlchemy. Auto-detection des changements de modèle. |
| **PostgreSQL 16** | RLS pour le multi-tenant, JSONB pour les données flexibles, partitioning pour les tables volumineuses (audit_logs, journal_entry_lines), extensions (pg_trgm pour la recherche, pgcrypto). |
| **Pydantic v2** | Validation stricte des entrées/sorties API, sérialisation, support `Decimal`, `date`, `datetime`, settings management. |
| **Celery + Redis** | Jobs asynchrones : calcul de paie en masse, génération PDF, imports, OCR, calcul TVA. Redis comme broker et cache. |
| **pytest** | Framework de test standard Python, fixtures puissantes, plugins (pytest-asyncio, pytest-cov, factory_boy). |

## 2.2 Frontend

| Choix | Justification |
|-------|---------------|
| **Next.js 14+ (App Router)** | SSR pour le SEO des pages publiques, RSC pour la performance, routing file-based, API routes pour les BFF patterns si nécessaire. |
| **TypeScript strict** | Sécurité de typage bout en bout. Les schémas Pydantic du backend sont convertis en types TypeScript via `openapi-typescript`. |
| **Tailwind CSS** | Utility-first, rapide à itérer, design system personnalisable, bundle minimal. |
| **shadcn/ui** | Composants accessibles (Radix primitives), copiés dans le projet (pas de dépendance externe), personnalisables. |
| **React Query (TanStack Query)** | Cache côté client, invalidation automatique, optimistic updates, pagination infinie, mutations. |
| **Zod** | Validation runtime des données côté client, cohérent avec Pydantic côté serveur. |
| **react-hook-form** | Performance (uncontrolled components), intégration Zod native, minimal re-renders. |
| **nuqs** | Synchronisation des filtres/tri/pagination avec l'URL query string. |

## 2.3 Infrastructure

| Choix | Justification |
|-------|---------------|
| **Docker + docker-compose** | Environnement de développement reproductible. Même stack en dev et en prod. |
| **Nginx/Caddy** | Reverse proxy, TLS termination, rate limiting, static files. Caddy pour le HTTPS automatique. |
| **MinIO** | Stockage S3-compatible self-hosted pour les documents. Migration vers AWS S3 / OVH Object Storage transparente. |
| **Redis** | Cache (sessions, règles métier, résultats de calcul), broker Celery, pub/sub pour les notifications temps réel. |
| **GitHub Actions** | CI/CD : lint, tests, build, deploy. Gratuit pour les repos privés (2000 min/mois). |

## 2.4 Contrainte : précision décimale

La comptabilité exige une précision parfaite. **Aucun float n'est utilisé** dans tout le système.

| Couche | Type utilisé |
|--------|-------------|
| PostgreSQL | `NUMERIC(15,2)` pour les montants, `NUMERIC(10,4)` pour les taux |
| SQLAlchemy | `sa.Numeric(precision=15, scale=2)` |
| Python | `decimal.Decimal` avec context `ROUND_HALF_UP` |
| Pydantic | `condecimal(max_digits=15, decimal_places=2)` |
| Frontend | `string` pour l'affichage (formatage via `Intl.NumberFormat`), `number` jamais pour les calculs de montants |
| API JSON | `string` pour les montants (ex: `"12345.67"`) — jamais de `number` JSON pour les montants |

---

# 3. Architecture backend détaillée

## 3.1 App factory et startup

```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    await init_redis()
    await init_event_bus()
    await load_rule_engine_cache()
    yield
    # Shutdown
    await close_database()
    await close_redis()

def create_app() -> FastAPI:
    app = FastAPI(
        title="EasyAccounting API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware (order matters - last added = first executed)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RBACMiddleware)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CORSMiddleware, ...)

    # Routers
    app.include_router(auth_router,       prefix="/api/v1/auth",       tags=["auth"])
    app.include_router(tenant_router,     prefix="/api/v1/tenants",    tags=["tenants"])
    app.include_router(company_router,    prefix="/api/v1/companies",  tags=["companies"])
    app.include_router(dossier_router,    prefix="/api/v1/dossiers",   tags=["dossiers"])
    app.include_router(accounting_router, prefix="/api/v1/accounting", tags=["accounting"])
    app.include_router(tva_router,        prefix="/api/v1/tva",        tags=["tva"])
    app.include_router(payroll_router,    prefix="/api/v1/payroll",    tags=["payroll"])
    app.include_router(commercial_router, prefix="/api/v1/commercial", tags=["commercial"])
    app.include_router(assets_router,     prefix="/api/v1/assets",     tags=["assets"])
    app.include_router(analytics_router,  prefix="/api/v1/analytics",  tags=["analytics"])
    app.include_router(reports_router,    prefix="/api/v1/reports",    tags=["reports"])
    app.include_router(documents_router,  prefix="/api/v1/documents",  tags=["documents"])
    app.include_router(rules_router,      prefix="/api/v1/rules",      tags=["rules"])
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])

    return app
```

## 3.2 Pattern par module : Service → Repository → Model

Chaque module métier suit une architecture en couches stricte :

```
Router (API) ──▶ Service (Business Logic) ──▶ Repository (Data Access) ──▶ Model (DB)
    │                    │                          │
    │ Pydantic           │ Domain Objects            │ SQLAlchemy Models
    │ Schemas            │ Rule Engine calls          │ Raw SQL when needed
    │ (validation)       │ Event emission             │
    │                    │ Audit logging              │
```

**Règle absolue** : le Router ne contient aucune logique métier. Le Service ne contient aucun SQL. Le Repository ne contient aucune règle métier.

### 3.2.1 Exemple — Module Accounting

```python
# app/modules/accounting/router.py
from fastapi import APIRouter, Depends, Query
from app.core.auth.dependencies import get_current_user, require_permission
from app.core.tenancy.dependencies import get_current_dossier
from .service import AccountingService
from .schemas import JournalEntryCreate, JournalEntryResponse, JournalEntryFilter

router = APIRouter()

@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=201,
)
async def create_journal_entry(
    payload: JournalEntryCreate,
    user=Depends(require_permission("accounting", "create")),
    dossier=Depends(get_current_dossier),
    service: AccountingService = Depends(),
):
    return await service.create_journal_entry(
        dossier_id=dossier.id,
        data=payload,
        user_id=user.id,
    )

@router.post("/journal-entries/{entry_id}/validate")
async def validate_journal_entry(
    entry_id: uuid.UUID,
    user=Depends(require_permission("accounting", "validate")),
    dossier=Depends(get_current_dossier),
    service: AccountingService = Depends(),
):
    return await service.validate_entry(
        dossier_id=dossier.id,
        entry_id=entry_id,
        user_id=user.id,
    )
```

```python
# app/modules/accounting/service.py
from decimal import Decimal
from app.core.events import EventBus, JournalEntryValidated
from app.core.audit import AuditService
from app.core.rules_engine import RuleEngine
from .repository import AccountingRepository
from .schemas import JournalEntryCreate

class AccountingService:
    def __init__(
        self,
        repo: AccountingRepository = Depends(),
        events: EventBus = Depends(),
        audit: AuditService = Depends(),
        rules: RuleEngine = Depends(),
    ):
        self.repo = repo
        self.events = events
        self.audit = audit
        self.rules = rules

    async def create_journal_entry(
        self,
        dossier_id: uuid.UUID,
        data: JournalEntryCreate,
        user_id: uuid.UUID,
    ) -> JournalEntry:
        # 1. Validate business rules
        self._validate_equilibrium(data.lines)
        await self._validate_accounts_exist(dossier_id, data.lines)
        await self._validate_period_open(dossier_id, data.date)

        # 2. Create in draft status
        entry = await self.repo.create_entry(
            dossier_id=dossier_id,
            data=data,
            status="draft",
        )

        # 3. Audit
        await self.audit.log(
            action="CREATE",
            object_type="journal_entry",
            object_id=entry.id,
            data_after=entry.dict(),
            user_id=user_id,
        )

        return entry

    async def validate_entry(
        self,
        dossier_id: uuid.UUID,
        entry_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> JournalEntry:
        entry = await self.repo.get_entry(dossier_id, entry_id)

        if entry.status != "draft":
            raise BusinessError("Only draft entries can be validated")

        # Assign sequential piece number
        piece_number = await self.repo.next_piece_number(
            dossier_id, entry.journal_id, entry.fiscal_year_id
        )

        entry = await self.repo.update_entry_status(
            entry_id=entry_id,
            status="validated",
            piece_number=piece_number,
            validated_by=user_id,
            validated_at=utcnow(),
        )

        # Emit domain event (consumed by TVA, Analytics, etc.)
        await self.events.publish(JournalEntryValidated(
            entry_id=entry.id,
            dossier_id=dossier_id,
            journal_id=entry.journal_id,
            date=entry.date,
            lines=[line.dict() for line in entry.lines],
        ))

        await self.audit.log(
            action="VALIDATE",
            object_type="journal_entry",
            object_id=entry.id,
            user_id=user_id,
        )

        return entry

    def _validate_equilibrium(self, lines):
        total_debit = sum(l.debit for l in lines)
        total_credit = sum(l.credit for l in lines)
        if total_debit != total_credit:
            raise BusinessError(
                f"Entry is unbalanced: debit={total_debit}, credit={total_credit}"
            )
```

## 3.3 Bus d'événements interne

```python
# app/core/events/bus.py
from typing import Callable, Dict, List, Type
from dataclasses import dataclass

@dataclass
class DomainEvent:
    """Base class for all domain events."""
    pass

@dataclass
class JournalEntryValidated(DomainEvent):
    entry_id: uuid.UUID
    dossier_id: uuid.UUID
    journal_id: uuid.UUID
    date: date
    lines: list

@dataclass
class PayrollPeriodValidated(DomainEvent):
    period_id: uuid.UUID
    dossier_id: uuid.UUID
    month: int
    year: int

@dataclass
class InvoiceIssued(DomainEvent):
    invoice_id: uuid.UUID
    dossier_id: uuid.UUID
    invoice_type: str  # "sale" | "purchase"
    lines: list

class EventBus:
    _handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: Type[DomainEvent], handler: Callable):
        cls._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: DomainEvent):
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {handler.__name__}: {e}")
                # Non-blocking: log error, don't break the caller
```

**Abonnements typiques** :

| Événement | Abonné | Action |
|-----------|--------|--------|
| `JournalEntryValidated` | TVA Service | Indexer les écritures avec TVA pour le calcul périodique |
| `JournalEntryValidated` | Analytics Service | Ventiler l'écriture si imputation analytique |
| `PayrollPeriodValidated` | Accounting Service | Générer les écritures de paie dans le journal PA |
| `InvoiceIssued` | Accounting Service | Générer l'écriture de vente/achat |
| `InvoiceIssued` | Stock Service | Déclencher le mouvement de stock (si BL lié) |
| `TVADeclarationValidated` | Accounting Service | Générer l'écriture de liquidation TVA |
| `DepreciationCalculated` | Accounting Service | Générer les écritures de dotation |

## 3.4 Gestion des transactions

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Règle de transaction** : chaque requête API = une transaction. Si le service doit émettre un événement ET sauvegarder, l'événement est émis APRÈS le commit réussi (outbox pattern simplifié). Pour les opérations longues (calcul de paie en masse), on utilise Celery avec des transactions par batch.

---

# 4. Architecture frontend détaillée

## 4.1 Structure du projet

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # Groupe : pages d'auth (login, register, reset)
│   │   │   ├── login/page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/              # Groupe : pages authentifiées
│   │   │   ├── layout.tsx            # Layout avec sidebar, header, dossier selector
│   │   │   ├── page.tsx              # Dashboard principal
│   │   │   ├── accounting/
│   │   │   │   ├── journal-entries/
│   │   │   │   │   ├── page.tsx      # Liste des écritures
│   │   │   │   │   ├── new/page.tsx  # Saisie
│   │   │   │   │   └── [id]/page.tsx # Détail
│   │   │   │   ├── chart-of-accounts/
│   │   │   │   ├── ledger/
│   │   │   │   ├── balance/
│   │   │   │   └── reports/
│   │   │   ├── tva/
│   │   │   ├── payroll/
│   │   │   ├── commercial/
│   │   │   ├── assets/
│   │   │   ├── analytics/
│   │   │   ├── reports/
│   │   │   ├── documents/
│   │   │   └── settings/
│   │   └── api/                      # API routes Next.js (BFF si besoin)
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   ├── layout/                   # Sidebar, Header, DossierSelector
│   │   ├── forms/                    # Formulaires réutilisables
│   │   ├── tables/                   # DataTable générique
│   │   ├── accounting/               # Composants spécifiques comptabilité
│   │   ├── payroll/                  # Composants spécifiques paie
│   │   └── commercial/               # Composants spécifiques commercial
│   │
│   ├── lib/
│   │   ├── api/                      # Client API (fetch wrapper + React Query hooks)
│   │   │   ├── client.ts             # Axios/fetch instance avec auth header
│   │   │   ├── accounting.ts         # useJournalEntries(), useCreateEntry()...
│   │   │   ├── payroll.ts
│   │   │   └── ...
│   │   ├── auth/                     # Auth context, token management
│   │   ├── tenant/                   # Tenant/dossier context
│   │   ├── hooks/                    # Custom hooks
│   │   ├── utils/                    # Formatters, validators
│   │   │   ├── format-amount.ts      # Formatage montants marocains
│   │   │   ├── format-date.ts        # Formatage dates JJ/MM/AAAA
│   │   │   └── decimal.ts            # String-based decimal ops
│   │   └── types/                    # Types générés depuis l'OpenAPI
│   │       └── generated.ts          # Auto-generated from openapi.json
│   │
│   ├── stores/                       # Zustand stores (si besoin)
│   │   ├── auth-store.ts
│   │   └── dossier-store.ts
│   │
│   └── styles/
│       └── globals.css               # Tailwind imports + custom tokens
│
├── public/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

## 4.2 Contexte global et dossier actif

```typescript
// src/lib/tenant/dossier-context.tsx
"use client";

import { createContext, useContext, useState } from "react";

interface DossierContext {
  currentDossierId: string | null;
  currentCompanyId: string | null;
  switchDossier: (dossierId: string) => void;
}

const DossierCtx = createContext<DossierContext>(null!);

export function DossierProvider({ children }: { children: React.ReactNode }) {
  const [currentDossierId, setCurrentDossierId] = useState<string | null>(null);
  const [currentCompanyId, setCurrentCompanyId] = useState<string | null>(null);

  const switchDossier = (dossierId: string) => {
    setCurrentDossierId(dossierId);
    // Persist in localStorage for page reload
    localStorage.setItem("ea_dossier_id", dossierId);
    // Invalidate all React Query caches
    queryClient.invalidateQueries();
  };

  return (
    <DossierCtx.Provider value={{ currentDossierId, currentCompanyId, switchDossier }}>
      {children}
    </DossierCtx.Provider>
  );
}

export const useDossier = () => useContext(DossierCtx);
```

## 4.3 Client API avec injection du contexte

```typescript
// src/lib/api/client.ts
import { useDossier } from "@/lib/tenant/dossier-context";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function apiClient<T>(
  path: string,
  options: RequestInit & { dossierId?: string } = {},
): Promise<T> {
  const token = getAccessToken();
  const dossierId = options.dossierId ?? getCurrentDossierId();

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(dossierId && { "X-Dossier-Id": dossierId }),
      ...options.headers,
    },
  });

  if (res.status === 401) {
    await refreshToken();
    return apiClient(path, options); // Retry once
  }

  if (!res.ok) {
    const error = await res.json();
    throw new ApiError(res.status, error.detail);
  }

  return res.json();
}
```

## 4.4 Génération automatique des types TypeScript

```bash
# Générer les types depuis l'OpenAPI spec du backend
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/types/generated.ts
```

Ce pipeline est exécuté dans le CI après chaque changement backend. Il garantit le typage bout en bout.

---

# 5. Architecture API

## 5.1 Conventions REST

| Convention | Détail |
|-----------|--------|
| **Base URL** | `/api/v1/` |
| **Format** | JSON, UTF-8 |
| **Montants** | `string` (ex: `"12345.67"`) — jamais `number` |
| **Dates** | `string` ISO 8601 (ex: `"2026-03-18"`) |
| **DateTimes** | `string` ISO 8601 avec timezone (ex: `"2026-03-18T14:30:00Z"`) |
| **IDs** | UUID v4 (`string`) |
| **Pagination** | `?page=1&page_size=50` → réponse `{ items: [], total: N, page: N, page_size: N }` |
| **Filtrage** | Query params : `?status=validated&date_from=2026-01-01&date_to=2026-03-31` |
| **Tri** | `?sort_by=date&sort_order=desc` |
| **Erreurs** | `{ "detail": "message", "code": "ERROR_CODE", "field": "field_name" }` |

## 5.2 Catalogue des endpoints principaux

### Socle

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login` | Connexion (email + password → JWT) |
| POST | `/auth/refresh` | Rafraîchir le token |
| POST | `/auth/mfa/verify` | Vérifier le code MFA |
| GET | `/tenants/me` | Informations du tenant courant |
| GET | `/companies` | Liste des sociétés |
| GET | `/dossiers` | Liste des dossiers accessibles |
| GET | `/dossiers/{id}` | Détail d'un dossier |
| GET | `/users` | Liste des utilisateurs |
| POST | `/users` | Créer un utilisateur |
| GET | `/roles` | Liste des rôles |

### Comptabilité

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/accounting/chart-of-accounts` | Plan comptable du dossier actif |
| POST | `/accounting/chart-of-accounts` | Ajouter un sous-compte |
| GET | `/accounting/journals` | Liste des journaux |
| GET | `/accounting/journal-entries` | Liste des écritures (paginée, filtrable) |
| POST | `/accounting/journal-entries` | Créer une écriture (brouillard) |
| GET | `/accounting/journal-entries/{id}` | Détail d'une écriture |
| PUT | `/accounting/journal-entries/{id}` | Modifier un brouillard |
| POST | `/accounting/journal-entries/{id}/validate` | Valider l'écriture |
| POST | `/accounting/journal-entries/{id}/reverse` | Extourner |
| POST | `/accounting/journal-entries/import` | Import Excel |
| GET | `/accounting/ledger` | Grand livre |
| GET | `/accounting/trial-balance` | Balance |
| POST | `/accounting/lettrage` | Lettrer des lignes |
| DELETE | `/accounting/lettrage/{group_id}` | Délettrer |
| POST | `/accounting/bank-reconciliation/import` | Importer un relevé |
| GET | `/accounting/bank-reconciliation/status` | État du rapprochement |
| GET | `/accounting/fiscal-years` | Liste des exercices |
| POST | `/accounting/fiscal-years` | Créer un exercice |
| GET | `/accounting/periods` | Périodes de l'exercice |
| POST | `/accounting/periods/{id}/lock` | Verrouiller une période |

### TVA & Fiscalité

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/tva/declarations` | Historique des déclarations |
| POST | `/tva/declarations/calculate` | Calculer la TVA d'une période |
| POST | `/tva/declarations/{id}/validate` | Valider la déclaration |
| GET | `/tva/declarations/{id}/pdf` | Télécharger le formulaire PDF |
| GET | `/accounting/financial-statements/balance-sheet` | Bilan |
| GET | `/accounting/financial-statements/income-statement` | CPC |
| GET | `/accounting/financial-statements/tax-return` | Liasse fiscale |
| GET | `/accounting/financial-statements/tax-return/xml` | EDI XML |

### Paie

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/payroll/employees` | Liste des salariés |
| POST | `/payroll/employees` | Créer un salarié |
| GET | `/payroll/employees/{id}` | Fiche salarié |
| PUT | `/payroll/employees/{id}` | Modifier un salarié |
| GET | `/payroll/periods` | Périodes de paie |
| POST | `/payroll/runs` | Lancer le calcul de paie |
| GET | `/payroll/runs/{id}` | Résultat du calcul |
| POST | `/payroll/runs/{id}/validate` | Valider la paie |
| GET | `/payroll/payslips` | Bulletins de paie |
| GET | `/payroll/payslips/{id}/pdf` | Télécharger un bulletin |
| POST | `/payroll/simulate` | Simulation brut ↔ net |
| GET | `/payroll/declarations/damancom` | Générer DAMANCOM |
| GET | `/payroll/declarations/9421` | Générer état 9421 |

### Commercial

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/commercial/customers` | Clients |
| GET | `/commercial/products` | Produits |
| POST | `/commercial/quotations` | Créer un devis |
| POST | `/commercial/orders` | Créer une commande |
| POST | `/commercial/deliveries` | Créer un BL |
| POST | `/commercial/invoices` | Créer une facture |
| POST | `/commercial/payments` | Enregistrer un règlement |
| GET | `/commercial/stock/levels` | Niveaux de stock |
| POST | `/commercial/stock/adjustments` | Inventaire/régularisation |

### Transverses

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/documents/upload` | Uploader un document |
| GET | `/documents/{id}` | Télécharger un document |
| GET | `/notifications` | Notifications de l'utilisateur |
| PUT | `/notifications/{id}/read` | Marquer comme lue |
| GET | `/audit-logs` | Journal d'audit (admin) |
| GET | `/rules/{domain}` | Règles par domaine |
| POST | `/rules/{code}/compute` | Exécuter un calcul de règle |
| GET | `/reports/dashboard` | Données du dashboard |

## 5.3 Gestion des erreurs

```python
# app/core/exceptions.py
from fastapi import HTTPException

class BusinessError(HTTPException):
    """Erreur métier (400)"""
    def __init__(self, detail: str, code: str = "BUSINESS_ERROR"):
        super().__init__(status_code=400, detail={"detail": detail, "code": code})

class NotFoundError(HTTPException):
    """Ressource non trouvée (404)"""
    def __init__(self, resource: str, id: str):
        super().__init__(status_code=404, detail={
            "detail": f"{resource} {id} not found",
            "code": "NOT_FOUND",
        })

class ForbiddenError(HTTPException):
    """Accès interdit (403)"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail={"detail": detail, "code": "FORBIDDEN"})

class ConflictError(HTTPException):
    """Conflit (409) - ex: écriture déjà validée"""
    def __init__(self, detail: str):
        super().__init__(status_code=409, detail={"detail": detail, "code": "CONFLICT"})
```

**Codes d'erreur métier standardisés** :

| Code | Signification |
|------|---------------|
| `ENTRY_UNBALANCED` | Écriture déséquilibrée |
| `PERIOD_LOCKED` | Période verrouillée |
| `ENTRY_ALREADY_VALIDATED` | Écriture déjà validée |
| `ACCOUNT_NOT_FOUND` | Compte inexistant |
| `FISCAL_YEAR_CLOSED` | Exercice clôturé |
| `INSUFFICIENT_STOCK` | Stock insuffisant |
| `PAYROLL_ALREADY_VALIDATED` | Paie déjà validée |

---

# 6. Architecture sécurité / auth / RBAC

## 6.1 Authentification

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Login   │────▶│  Verify  │────▶│  Issue   │────▶│  Access  │
│  email + │     │  password│     │  JWT     │     │  granted │
│  password│     │  (argon2)│     │  pair    │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │                                   │
                      ▼ (si MFA activé)                   │
                ┌──────────┐                              │
                │  Verify  │──────────────────────────────┘
                │  TOTP    │
                └──────────┘
```

**JWT payload** :

```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "email": "user@example.com",
  "role": "collaborateur",
  "permissions": ["accounting:read", "accounting:create", "accounting:validate"],
  "dossier_ids": ["dossier_uuid_1", "dossier_uuid_2"],
  "exp": 1711234567,
  "iat": 1711233667
}
```

**Tokens** :

| Token | Durée | Stockage | Refresh |
|-------|-------|----------|---------|
| Access token | 15 min | Memory (JS) | Via refresh token |
| Refresh token | 7 jours | HttpOnly cookie + DB (whitelist) | Rotation à chaque usage |

**Sécurité** :
- Mot de passe : argon2id, minimum 10 caractères, complexité configurable.
- Rate limiting login : 5 tentatives / 15 min / IP + email.
- Verrouillage automatique après 5 échecs (déverrouillage par admin).
- MFA TOTP obligatoire pour le rôle Administrateur.
- Refresh token rotation : chaque refresh invalide l'ancien token.

## 6.2 RBAC (Role-Based Access Control)

### Modèle de permissions

```
Rôle
├── permissions[] : ["module:action", ...]
└── scope : "all_dossiers" | "assigned_dossiers"

Permission = "{module}:{action}"
  module : auth | accounting | tva | closing | payroll | commercial | assets | analytics | reports | documents | admin | rules
  action : read | create | update | delete | validate | export
```

### Rôles prédéfinis

| Rôle | Permissions clés | Scope |
|------|-----------------|-------|
| `admin` | Tout | all_dossiers |
| `expert_comptable` | Tout sauf admin | all_dossiers |
| `collaborateur` | accounting:*, tva:*, assets:*, documents:* (pas validate pour closing) | assigned_dossiers |
| `gestionnaire_paie` | payroll:*, documents:read | assigned_dossiers |
| `commercial` | commercial:*, documents:read | assigned_dossiers |
| `lecture_seule` | *:read, *:export | assigned_dossiers |

### Middleware RBAC

```python
# app/core/rbac/middleware.py
from fastapi import Request, Depends
from app.core.auth.dependencies import get_current_user

def require_permission(module: str, action: str):
    async def checker(request: Request, user=Depends(get_current_user)):
        required = f"{module}:{action}"
        if required not in user.permissions:
            raise ForbiddenError(f"Permission required: {required}")

        # Scope check: if scope is "assigned_dossiers", verify dossier_id
        dossier_id = request.headers.get("X-Dossier-Id")
        if user.scope == "assigned_dossiers" and dossier_id:
            if dossier_id not in user.dossier_ids:
                raise ForbiddenError("Access to this dossier is denied")

        return user
    return checker
```

## 6.3 Sécurité applicative

| Mesure | Implémentation |
|--------|---------------|
| **SQL Injection** | SQLAlchemy ORM (parameterized queries). Jamais de SQL brut avec interpolation de strings. |
| **XSS** | React escape par défaut. CSP headers stricts. Pas de `dangerouslySetInnerHTML`. |
| **CSRF** | SameSite=Lax cookies. Token CSRF pour les mutations si cookies utilisés. |
| **CORS** | Whitelist stricte des origines autorisées. |
| **Rate limiting** | Par IP (Nginx) + par user (Redis). |
| **Input validation** | Pydantic côté serveur, Zod côté client. Toute entrée est validée. |
| **File upload** | Validation MIME type, taille max (20 MB), scan antivirus (ClamAV en V2). |
| **Secrets** | `.env` (jamais commité), Docker secrets en prod. |
| **Headers de sécurité** | HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy. |

---

# 7. Architecture multi-tenant

## 7.1 Stratégie : Shared database, shared schema, RLS

Après analyse des options :

| Stratégie | Isolation | Complexité | Scalabilité | Choix |
|-----------|----------|------------|-------------|-------|
| DB par tenant | Forte | Très haute | Limitée (gestion de centaines de DB) | Non |
| Schema par tenant | Forte | Haute | Limitée (migrations sur N schemas) | Non |
| **Shared schema + RLS** | Forte (si bien implémenté) | Moyenne | Très bonne | **Oui** |

**Justification** : pour un SaaS avec potentiellement 1000+ tenants (cabinets + PME), la gestion de milliers de schémas ou bases est un cauchemar opérationnel. RLS offre une isolation forte au niveau de PostgreSQL, avec des performances excellentes grâce aux index partiels.

## 7.2 Implémentation RLS

```sql
-- Activation RLS sur chaque table
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;

-- Policy: chaque utilisateur ne voit que les données de son tenant
CREATE POLICY tenant_isolation ON journal_entries
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Index partiel pour la performance
CREATE INDEX idx_journal_entries_tenant
    ON journal_entries (tenant_id, dossier_id, date);
```

```python
# app/core/tenancy/middleware.py
class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract tenant_id from JWT (already verified by AuthMiddleware)
        tenant_id = request.state.user.tenant_id

        # Set PostgreSQL session variable for RLS
        async with get_db_session() as session:
            await session.execute(
                text("SET app.current_tenant_id = :tid"),
                {"tid": str(tenant_id)},
            )
            request.state.db = session
            request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response
```

## 7.3 Mixin SQLAlchemy pour le tenant

```python
# app/shared/models.py
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey
import uuid

class Base(DeclarativeBase):
    pass

class TenantMixin:
    """Mixin ajouté à TOUTES les tables multi-tenant."""
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

class AuditMixin:
    """Mixin pour le soft-delete et les timestamps."""
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
```

## 7.4 Contexte du dossier

En plus du `tenant_id`, la plupart des requêtes comptables nécessitent un `dossier_id` :

```python
# app/core/tenancy/dependencies.py
async def get_current_dossier(
    request: Request,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dossier:
    dossier_id = request.headers.get("X-Dossier-Id")
    if not dossier_id:
        raise BusinessError("X-Dossier-Id header is required")

    # Verify user has access to this dossier
    if user.scope == "assigned_dossiers" and dossier_id not in user.dossier_ids:
        raise ForbiddenError("Access denied to this dossier")

    dossier = await db.get(Dossier, uuid.UUID(dossier_id))
    if not dossier or dossier.tenant_id != user.tenant_id:
        raise NotFoundError("Dossier", dossier_id)

    return dossier
```

---

# 8. Architecture documentaire

## 8.1 Flux de stockage

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ Client     │───▶│ FastAPI    │───▶│ Validation │───▶│   MinIO    │
│ (upload)   │    │ multipart  │    │ - MIME     │    │   (S3)     │
│            │    │ form-data  │    │ - Size ≤20M│    │            │
└────────────┘    └────────────┘    │ - Extension│    └──────┬─────┘
                                    └────────────┘           │
                                                             ▼
                                                    ┌────────────────┐
                                                    │ PostgreSQL     │
                                                    │ documents table│
                                                    │ (métadonnées)  │
                                                    └────────────────┘
```

## 8.2 Structure de stockage MinIO

```
bucket: easyaccounting-documents
├── {tenant_id}/
│   ├── {dossier_id}/
│   │   ├── accounting/
│   │   │   ├── {year}/
│   │   │   │   ├── {entry_id}_{filename}.pdf
│   │   │   │   └── ...
│   │   ├── payroll/
│   │   │   ├── {year}/
│   │   │   │   ├── payslip_{employee_id}_{period}.pdf
│   │   │   │   └── ...
│   │   ├── commercial/
│   │   │   ├── invoices/
│   │   │   └── ...
│   │   └── general/
│   │       └── ...
│   └── ...
└── ...
```

## 8.3 Modèle de données documents

```python
class Document(Base, TenantMixin, AuditMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    filename: Mapped[str]                          # Nom original
    storage_key: Mapped[str]                       # Chemin MinIO
    mime_type: Mapped[str]                         # application/pdf, image/jpeg...
    size_bytes: Mapped[int]
    document_type: Mapped[str | None]              # invoice_purchase, invoice_sale, bank_statement, payslip, contract, other
    ocr_text: Mapped[str | None]                   # Texte OCR extrait
    ocr_metadata: Mapped[dict | None] = mapped_column(JSONB)  # Champs extraits par l'IA
    classification_confidence: Mapped[Decimal | None]

class DocumentLink(Base):
    __tablename__ = "document_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    linked_type: Mapped[str]                       # journal_entry, payslip, invoice, employee
    linked_id: Mapped[uuid.UUID]
```

---

# 9. Architecture des notifications

## 9.1 Types et canaux

```python
class NotificationType(str, Enum):
    REGULATORY_DEADLINE = "regulatory_deadline"   # Échéance réglementaire
    PAYROLL_ALERT = "payroll_alert"               # Alerte paie (fin CDD, etc.)
    COMMERCIAL_ALERT = "commercial_alert"         # Facture en retard, stock min
    ACCOUNTING_ALERT = "accounting_alert"         # Écriture brouillard ancienne
    SECURITY_ALERT = "security_alert"             # Connexion, MFA, mot de passe
    SYSTEM_INFO = "system_info"                   # MAJ, maintenance
    WORKFLOW_ACTION = "workflow_action"            # Approbation requise

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
```

## 9.2 Flux de notification

```
┌──────────────┐    ┌───────────────┐    ┌───────────────┐
│ Événement    │───▶│ Notification  │───▶│ Channels      │
│ métier       │    │ Service       │    │               │
│ (EventBus)   │    │               │    │ ┌─── In-App   │
│              │    │ - Résolution  │    │ │   (DB)      │
│              │    │   des règles  │    │ │              │
│              │    │ - Résolution  │    │ ├─── Email    │
│              │    │   des dest.   │    │ │   (SMTP/   │
│              │    │ - Template    │    │ │    Celery)  │
│              │    │   rendering   │    │ │              │
│              │    │               │    │ └─── WebSocket│
│              │    │               │    │     (V3)      │
└──────────────┘    └───────────────┘    └───────────────┘
```

## 9.3 Notifications in-app (temps réel V1)

En V1, polling simple : le frontend fait un `GET /notifications?unread=true` toutes les 30 secondes.

En V3, WebSocket via FastAPI :
```python
@router.websocket("/ws/notifications")
async def notification_ws(websocket: WebSocket, user=Depends(ws_auth)):
    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"notifications:{user.id}")
    async for message in pubsub.listen():
        await websocket.send_json(message)
```

---

# 10. Architecture reporting / exports

## 10.1 Génération PDF

| Outil | Usage | Justification |
|-------|-------|---------------|
| **WeasyPrint** | États financiers (bilan, CPC, balance, grand livre) | Rendering HTML → PDF, support CSS paged media, tables complexes |
| **reportlab** | Bulletins de paie, factures, DAMANCOM | Contrôle pixel-perfect, formulaires pré-formatés |
| **openpyxl** | Export Excel | Génération native Excel avec formatage |

## 10.2 Flux de génération

```
┌──────────────┐    ┌───────────────┐    ┌───────────────┐    ┌──────────┐
│ API Request  │───▶│ Report        │───▶│ Data          │───▶│ Template │
│ GET /reports │    │ Service       │    │ Aggregation   │    │ Engine   │
│ /balance-    │    │               │    │ (SQL queries) │    │ (Jinja2) │
│ sheet?format │    │               │    │               │    │          │
│ =pdf         │    │               │    │               │    │          │
└──────────────┘    └───────────────┘    └───────────────┘    └────┬─────┘
                                                                   │
                                                                   ▼
                                                            ┌──────────────┐
                                                            │ PDF/Excel    │
                                                            │ Renderer     │
                                                            │ (WeasyPrint/ │
                                                            │  openpyxl)   │
                                                            └──────┬───────┘
                                                                   │
                                                                   ▼
                                                            ┌──────────────┐
                                                            │ StreamingRes │
                                                            │ ou MinIO     │
                                                            │ (si async)   │
                                                            └──────────────┘
```

Pour les rapports lourds (bilan d'un dossier avec 100k écritures), la génération est déléguée à Celery. Le frontend reçoit un `job_id` et poll le statut.

## 10.3 EDI XML (Liasse fiscale DGI)

```python
# app/modules/tva/edi_generator.py
from lxml import etree

class EDIXMLGenerator:
    def __init__(self, xsd_path: str):
        self.schema = etree.XMLSchema(etree.parse(xsd_path))

    def generate(self, liasse_data: LiasseData) -> bytes:
        root = etree.Element("DeclarationFiscale")
        # Build XML tree from liasse_data...
        self._add_bilan(root, liasse_data.bilan)
        self._add_cpc(root, liasse_data.cpc)
        # ... all tableaux A to J

        # Validate against XSD
        if not self.schema.validate(root):
            errors = self.schema.error_log
            raise BusinessError(f"EDI XML validation failed: {errors}")

        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
```

---

# 11. Architecture IA

## 11.1 Architecture des services IA

```
┌────────────────────────────────────────────────────────┐
│                    AI SERVICE LAYER                      │
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  OCR Service     │    │  Classification  │          │
│  │                  │    │  Service         │          │
│  │  - Tesseract     │    │                  │          │
│  │    (self-hosted) │    │  - scikit-learn  │          │
│  │  - Azure Doc     │    │    classifier    │          │
│  │    Intelligence  │    │  - Per-dossier   │          │
│  │    (cloud)       │    │    model         │          │
│  └────────┬─────────┘    └────────┬─────────┘          │
│           │                       │                      │
│  ┌────────▼───────────────────────▼─────────┐          │
│  │            Suggestion Service             │          │
│  │                                           │          │
│  │  - Account suggestion (frequency-based)   │          │
│  │  - Lettrage suggestion (pattern-based)    │          │
│  │  - Anomaly detection (statistical)        │          │
│  └────────────────────┬──────────────────────┘          │
│                       │                                  │
│  ┌────────────────────▼──────────────────────┐          │
│  │            Confidence Scorer              │          │
│  │                                           │          │
│  │  Score > 90% → auto-fill (opt-out)        │          │
│  │  Score 70-90% → suggest (opt-in)          │          │
│  │  Score < 70% → manual                     │          │
│  └───────────────────────────────────────────┘          │
│                                                          │
│  ┌───────────────────────────────────────────┐          │
│  │            Learning Feedback Loop         │          │
│  │                                           │          │
│  │  User accepts suggestion → +1 weight      │          │
│  │  User corrects suggestion → retrain       │          │
│  │  Per-dossier model (not cross-tenant)     │          │
│  └───────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────┘
```

## 11.2 Implémentation OCR

```python
# app/core/ai/ocr_service.py
class OCRService:
    async def extract_invoice(self, document_id: uuid.UUID) -> InvoiceExtraction:
        document = await self.doc_repo.get(document_id)
        file_bytes = await self.storage.download(document.storage_key)

        # 1. OCR
        raw_text = await self._run_ocr(file_bytes, document.mime_type)

        # 2. Structured extraction (NLP/regex hybrid)
        extracted = self._extract_fields(raw_text)
        # Fields: supplier_name, supplier_ice, invoice_number, invoice_date,
        #         amount_ht, tva_details[], amount_ttc

        # 3. Confidence scoring per field
        scored = self._score_confidence(extracted, raw_text)

        # 4. Account suggestion based on history
        if scored.supplier_name.confidence > 0.7:
            suggested_accounts = await self._suggest_accounts(
                dossier_id=document.dossier_id,
                supplier_name=scored.supplier_name.value,
            )
            scored.suggested_accounts = suggested_accounts

        # 5. Store result
        await self.doc_repo.update_ocr_metadata(document_id, scored.dict())

        return scored
```

## 11.3 Modèle de suggestion d'imputation

Le modèle est simple et déterministe pour commencer (pas de deep learning) :

1. **Recherche historique** : pour un fournisseur donné dans ce dossier, quel compte a été utilisé le plus souvent ?
2. **Score de fréquence** : si le compte X a été utilisé 42 fois sur 45 écritures pour ce fournisseur → confiance = 42/45 = 93%.
3. **Fallback par libellé** : si le fournisseur est inconnu, analyse du libellé par mots-clés (ex: "loyer" → 6131, "téléphone" → 6145).
4. **Apprentissage** : chaque validation ou correction alimente le compteur.

```sql
-- Table de fréquence des imputations (matérialized view ou table alimentée par événement)
CREATE TABLE account_suggestion_stats (
    tenant_id UUID NOT NULL,
    dossier_id UUID NOT NULL,
    third_party_id UUID,
    label_pattern TEXT,
    account_id UUID NOT NULL,
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMP,
    PRIMARY KEY (tenant_id, dossier_id, third_party_id, account_id)
);
```

## 11.4 Isolation des données IA

**Règle fondamentale** : les modèles IA sont entraînés PAR DOSSIER (ou par tenant au maximum). Jamais de données cross-tenant dans l'entraînement. L'apprentissage d'un cabinet ne bénéficie pas à un autre cabinet.

---

# 12. Architecture du moteur de règles

## 12.1 Rôle

Le moteur de règles est le composant central qui :
- Stocke toutes les constantes réglementaires marocaines (barèmes IR, taux CNSS, taux TVA, SMIG, durées d'amortissement).
- Stocke les paramètres configurables par entreprise (taux CIMR, taux mutuelle, rubriques personnalisées).
- Fournit une API de calcul consommée par les modules métier.
- Gère le versioning avec date d'effet (un calcul de paie de janvier 2026 utilise les règles en vigueur en janvier 2026).
- Journalise chaque décision de calcul pour l'auditabilité.

## 12.2 Structure des règles

```python
# app/core/rules_engine/models.py

class RuleCategory(str, Enum):
    TAX_IR = "tax_ir"                  # Barème IR
    TAX_TVA = "tax_tva"                # Taux TVA
    TAX_IS = "tax_is"                  # Barème IS
    SOCIAL_CNSS = "social_cnss"        # Taux CNSS
    SOCIAL_AMO = "social_amo"          # Taux AMO
    SOCIAL_CIMR = "social_cimr"        # Taux CIMR
    SOCIAL_MUTUELLE = "social_mutuelle"
    PAYROLL_SMIG = "payroll_smig"      # SMIG
    PAYROLL_SENIORITY = "payroll_seniority"  # Prime ancienneté
    PAYROLL_OVERTIME = "payroll_overtime"     # Heures sup
    PAYROLL_LEAVE = "payroll_leave"          # Congés
    PAYROLL_SEVERANCE = "payroll_severance"  # Indemnités licenciement
    DEPRECIATION = "depreciation"       # Durées et méthodes d'amortissement
    ACCOUNTING = "accounting"           # Règles comptables

class RuleScope(str, Enum):
    NATIONAL = "national"              # Réglementaire, non modifiable par l'utilisateur
    ENTERPRISE = "enterprise"          # Configurable par société

class RuleValueType(str, Enum):
    SCALAR = "scalar"                  # Valeur unique (ex: SMIG = 3111.39)
    RATE = "rate"                      # Taux (ex: AMO salariale = 2.26%)
    BRACKET_TABLE = "bracket_table"    # Barème par tranches (ex: IR)
    RATE_TABLE = "rate_table"          # Table de taux (ex: CNSS)
    DURATION_TABLE = "duration_table"  # Table de durées (ex: amortissements)
    FORMULA = "formula"                # Formule de calcul (ex: rubrique personnalisée)

class Rule(Base, TenantMixin):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(unique=True)         # ex: "IR_BAREME_2026"
    category: Mapped[RuleCategory]
    scope: Mapped[RuleScope]
    value_type: Mapped[RuleValueType]
    description: Mapped[str]
    company_id: Mapped[uuid.UUID | None]                    # NULL for national rules

class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rules.id"))
    version: Mapped[int]
    effective_from: Mapped[date]                            # Date d'effet
    effective_to: Mapped[date | None]                       # NULL = en vigueur
    value: Mapped[dict] = mapped_column(JSONB)              # Valeur structurée
    modified_by: Mapped[uuid.UUID | None]
    modified_at: Mapped[datetime]
    modification_reason: Mapped[str | None]
```

## 12.3 Exemples de valeurs stockées

### Barème IR (bracket_table)

```json
{
  "brackets": [
    { "min": 0,      "max": 30000,  "rate": 0.00, "deduction": 0 },
    { "min": 30001,  "max": 50000,  "rate": 0.10, "deduction": 3000 },
    { "min": 50001,  "max": 60000,  "rate": 0.20, "deduction": 8000 },
    { "min": 60001,  "max": 80000,  "rate": 0.30, "deduction": 14000 },
    { "min": 80001,  "max": 180000, "rate": 0.34, "deduction": 17200 },
    { "min": 180001, "max": null,   "rate": 0.38, "deduction": 24400 }
  ],
  "annual": true,
  "professional_expenses_rate": 0.20,
  "professional_expenses_cap_monthly": 2500,
  "dependent_deduction_monthly": 30,
  "dependent_max": 6
}
```

### Taux CNSS (rate_table)

```json
{
  "contributions": [
    { "code": "PREST_SOCIAL_CT", "employee_rate": 0,      "employer_rate": 0.0105, "ceiling": null },
    { "code": "PREST_SOCIAL_LT", "employee_rate": 0.0396, "employer_rate": 0.0793, "ceiling": 6000 },
    { "code": "ALLOC_FAMILIALES","employee_rate": 0,      "employer_rate": 0.064,  "ceiling": null },
    { "code": "AMO",            "employee_rate": 0.0226, "employer_rate": 0.0452, "ceiling": null },
    { "code": "TAXE_FP",        "employee_rate": 0,      "employer_rate": 0.016,  "ceiling": null }
  ]
}
```

### Durées d'amortissement (duration_table)

```json
{
  "categories": [
    { "code": "TERRAIN",      "label": "Terrains",                   "duration_years": null, "method": "none" },
    { "code": "CONSTRUCTION", "label": "Constructions",              "duration_years": 20,   "method": "linear" },
    { "code": "MATERIEL_IND", "label": "Matériel industriel",        "duration_years": 10,   "method": "linear" },
    { "code": "MATERIEL_TR",  "label": "Matériel de transport",      "duration_years": 5,    "method": "linear" },
    { "code": "MOBILIER",     "label": "Mobilier de bureau",         "duration_years": 10,   "method": "linear" },
    { "code": "MATERIEL_INF", "label": "Matériel informatique",      "duration_years": 5,    "method": "linear" },
    { "code": "LOGICIEL",     "label": "Logiciels",                  "duration_years": 5,    "method": "linear" },
    { "code": "AMENAGEMENT",  "label": "Aménagements et agencements","duration_years": 10,   "method": "linear" }
  ],
  "degressive_coefficients": [
    { "duration_min": 3, "duration_max": 4, "coefficient": 1.5 },
    { "duration_min": 5, "duration_max": 6, "coefficient": 2.0 },
    { "duration_min": 7, "duration_max": 999, "coefficient": 3.0 }
  ]
}
```

## 12.4 Moteur d'exécution

```python
# app/core/rules_engine/engine.py
from datetime import date
from decimal import Decimal

class RuleEngine:
    def __init__(self, repo: RuleRepository, cache: Redis):
        self.repo = repo
        self.cache = cache

    async def get_rule_value(
        self,
        code: str,
        reference_date: date,
        company_id: uuid.UUID | None = None,
    ) -> dict:
        """Résout la valeur d'une règle à une date donnée."""
        cache_key = f"rule:{code}:{reference_date}:{company_id or 'national'}"
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Priority: enterprise rule > national rule
        if company_id:
            version = await self.repo.get_active_version(
                code=code, reference_date=reference_date, company_id=company_id,
            )
            if version:
                await self.cache.set(cache_key, json.dumps(version.value), ex=3600)
                return version.value

        version = await self.repo.get_active_version(
            code=code, reference_date=reference_date, company_id=None,
        )
        if not version:
            raise BusinessError(f"No rule found for code={code} at date={reference_date}")

        await self.cache.set(cache_key, json.dumps(version.value), ex=3600)
        return version.value

    async def compute_ir(
        self,
        gross_taxable_monthly: Decimal,
        cnss_employee: Decimal,
        cimr_employee: Decimal,
        mutual_employee: Decimal,
        dependents: int,
        reference_date: date,
    ) -> IRComputeResult:
        """Calcule l'IR mensuel selon le barème en vigueur."""
        rule = await self.get_rule_value("IR_BAREME", reference_date)
        brackets = rule["brackets"]

        # 1. Frais professionnels
        prof_exp_rate = Decimal(str(rule["professional_expenses_rate"]))
        prof_exp_cap = Decimal(str(rule["professional_expenses_cap_monthly"]))
        frais_pro = min(gross_taxable_monthly * prof_exp_rate, prof_exp_cap)

        # 2. Salaire Net Imposable mensuel
        sni_monthly = (
            gross_taxable_monthly
            - frais_pro
            - cnss_employee
            - cimr_employee
            - mutual_employee
        )

        # 3. SNI annualisé pour le barème
        sni_annual = sni_monthly * 12

        # 4. Application du barème
        ir_annual = Decimal("0")
        for bracket in brackets:
            b_min = Decimal(str(bracket["min"]))
            b_max = Decimal(str(bracket["max"])) if bracket["max"] else Decimal("999999999")
            rate = Decimal(str(bracket["rate"]))
            deduction = Decimal(str(bracket["deduction"]))

            if sni_annual >= b_min:
                ir_annual = sni_annual * rate - deduction
                # Last matching bracket wins (progressive)

        # 5. IR mensuel
        ir_monthly = ir_annual / 12

        # 6. Déduction personnes à charge
        dep_deduction = Decimal(str(rule["dependent_deduction_monthly"]))
        dep_max = int(rule["dependent_max"])
        ir_monthly -= dep_deduction * min(dependents, dep_max)

        # 7. Plancher à 0
        ir_monthly = max(ir_monthly, Decimal("0"))

        return IRComputeResult(
            sni_monthly=sni_monthly,
            ir_monthly=ir_monthly.quantize(Decimal("0.01")),
            frais_professionnels=frais_pro,
            dependents_deduction=dep_deduction * min(dependents, dep_max),
            bracket_applied=self._find_bracket(sni_annual, brackets),
        )

    async def compute_cnss(
        self,
        gross_cotisable: Decimal,
        reference_date: date,
    ) -> CNSSComputeResult:
        """Calcule les cotisations CNSS."""
        rule = await self.get_rule_value("CNSS_RATES", reference_date)
        results = []
        for contrib in rule["contributions"]:
            ceiling = Decimal(str(contrib["ceiling"])) if contrib["ceiling"] else None
            base = min(gross_cotisable, ceiling) if ceiling else gross_cotisable
            employee = base * Decimal(str(contrib["employee_rate"]))
            employer = base * Decimal(str(contrib["employer_rate"]))
            results.append(CNSSLine(
                code=contrib["code"],
                base=base,
                employee_amount=employee.quantize(Decimal("0.01")),
                employer_amount=employer.quantize(Decimal("0.01")),
            ))
        return CNSSComputeResult(lines=results)
```

## 12.5 Ce qui est déterministe vs ce qui est suggéré

| Calcul | Nature | Explication |
|--------|--------|-------------|
| IR (barème progressif) | **Déterministe** | Résultat unique et certain pour des paramètres donnés |
| CNSS (cotisations) | **Déterministe** | Taux × base, pas d'ambiguïté |
| TVA (taux par opération) | **Déterministe** | Le taux est déterminé par la nature de l'opération |
| Amortissement (dotation) | **Déterministe** | Valeur / durée, prorata temporis |
| Prime d'ancienneté | **Déterministe** | Barème légal clair |
| Suggestion de compte comptable | **Suggéré (IA)** | Probabilité basée sur l'historique, l'utilisateur tranche |
| Classification de document | **Suggéré (IA)** | Confiance variable, validation humaine requise |
| Lettrage automatique | **Suggéré (IA)** | Correspondance probabiliste, l'utilisateur confirme |
| Anomalies détectées | **Suggéré (IA)** | Signal à investiguer, pas une certitude |
| Imputation analytique | **Suggéré ou Déterministe** | Déterministe si règle par défaut configurée, suggéré sinon |

## 12.6 Simulation ("what-if")

```python
async def simulate_rule_change(
    self,
    code: str,
    new_value: dict,
    dossier_id: uuid.UUID,
    period: str,  # "2026-03"
) -> SimulationResult:
    """Simule l'impact d'un changement de règle sur un dossier."""
    # Ex: simuler un nouveau barème IR sur la masse salariale
    current_result = await self._compute_payroll_with_rules(dossier_id, period, use_current=True)
    simulated_result = await self._compute_payroll_with_rules(dossier_id, period, override={code: new_value})

    return SimulationResult(
        current=current_result,
        simulated=simulated_result,
        delta=simulated_result.total - current_result.total,
        affected_employees=simulated_result.affected_count,
    )
```

## 12.7 Journal de décision

Chaque appel au moteur de règles est journalisé :

```python
class RuleDecisionLog(Base, TenantMixin):
    __tablename__ = "rule_decision_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_code: Mapped[str]
    rule_version_id: Mapped[uuid.UUID]
    reference_date: Mapped[date]
    input_params: Mapped[dict] = mapped_column(JSONB)   # Paramètres d'entrée
    output_result: Mapped[dict] = mapped_column(JSONB)  # Résultat du calcul
    context_type: Mapped[str]                            # "payroll", "tva", "depreciation"
    context_id: Mapped[uuid.UUID]                        # ID du bulletin, déclaration, etc.
    computed_at: Mapped[datetime]
```

Cela permet de répondre à la question : "Pourquoi l'IR de ce salarié est-il de X MAD en mars 2026 ?" → consultation du journal de décision avec les paramètres d'entrée et la version du barème utilisée.

## 12.8 Interface d'administration

| Écran | Fonctionnalité |
|-------|---------------|
| **Catalogue des règles** | Liste de toutes les règles par catégorie, valeur en vigueur, date d'effet |
| **Détail d'une règle** | Historique des versions, valeur actuelle, éditeur de valeur (formulaire adapté au `value_type`) |
| **Modification d'une règle entreprise** | Formulaire avec date d'effet obligatoire, motif, preview de l'impact |
| **Notification de MAJ réglementaire** | Alerte quand l'éditeur pousse une nouvelle version d'une règle nationale |
| **Simulateur** | Interface "what-if" pour tester un changement avant de l'appliquer |

## 12.9 Interaction avec l'IA

Le moteur de règles est **déterministe**. L'IA est **probabiliste**. Ils interagissent ainsi :

1. L'IA extrait des données d'un document (ex: montant HT, taux TVA).
2. Le moteur de règles valide que le taux TVA extrait est un taux légal (20%, 14%, 10%, 7%, 0%).
3. Si le taux extrait n'est pas un taux légal → l'IA ajuste ou signale une anomalie.
4. Pour le calcul de paie : l'IA peut suggérer des éléments variables (HS estimées, primes récurrentes), mais le calcul lui-même est 100% déterministe via le moteur de règles.

---

# 13. Modèle de données de haut niveau

## 13.1 Socle

```python
class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    plan: Mapped[str]                      # "starter", "pro", "enterprise"
    status: Mapped[str]                    # "active", "suspended", "frozen", "terminated"
    created_at: Mapped[datetime]
    suspended_at: Mapped[datetime | None]
    settings: Mapped[dict] = mapped_column(JSONB, default={})

class Company(Base, TenantMixin, AuditMixin):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]                      # Raison sociale
    legal_form: Mapped[str | None]         # SARL, SA, SNC, auto-entrepreneur...
    ice: Mapped[str]                       # Identifiant Commun Entreprise (15 chars)
    if_number: Mapped[str | None]          # Identifiant Fiscal
    rc_number: Mapped[str | None]          # Registre du Commerce
    patente: Mapped[str | None]
    cnss_employer: Mapped[str | None]      # Numéro CNSS employeur
    capital: Mapped[Decimal | None]
    address: Mapped[dict] = mapped_column(JSONB)  # {street, city, zip, country}
    phone: Mapped[str | None]
    email: Mapped[str | None]
    logo_document_id: Mapped[uuid.UUID | None]
    accounting_model: Mapped[str]          # "normal", "simplified"
    default_currency: Mapped[str] = mapped_column(default="MAD")
    fiscal_year_start_month: Mapped[int] = mapped_column(default=1)

class Dossier(Base, TenantMixin, AuditMixin):
    __tablename__ = "dossiers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"))
    name: Mapped[str]
    status: Mapped[str]                    # "active", "archived"
    current_fiscal_year_id: Mapped[uuid.UUID | None]

class FiscalYear(Base, TenantMixin, AuditMixin):
    __tablename__ = "fiscal_years"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    start_date: Mapped[date]
    end_date: Mapped[date]
    status: Mapped[str]                    # "open", "pre_closing", "closed", "reopened"
    closed_by: Mapped[uuid.UUID | None]
    closed_at: Mapped[datetime | None]
    reopened_by: Mapped[uuid.UUID | None]
    reopened_at: Mapped[datetime | None]
    reopen_reason: Mapped[str | None]

class AccountingPeriod(Base, TenantMixin):
    __tablename__ = "accounting_periods"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fiscal_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fiscal_years.id"))
    month: Mapped[int]
    start_date: Mapped[date]
    end_date: Mapped[date]
    is_locked: Mapped[bool] = mapped_column(default=False)
    locked_by: Mapped[uuid.UUID | None]
    locked_at: Mapped[datetime | None]

class User(Base, TenantMixin, AuditMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str]
    password_hash: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str | None]
    status: Mapped[str]                    # "active", "inactive", "suspended", "locked"
    mfa_enabled: Mapped[bool] = mapped_column(default=False)
    mfa_secret: Mapped[str | None]
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    last_login_at: Mapped[datetime | None]

class Role(Base, TenantMixin):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    is_system: Mapped[bool] = mapped_column(default=False)  # Prédéfini, non supprimable
    permissions: Mapped[list] = mapped_column(JSONB)         # ["accounting:read", "accounting:create", ...]
    scope: Mapped[str]                     # "all_dossiers", "assigned_dossiers"

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)

class UserDossierAssignment(Base):
    __tablename__ = "user_dossier_assignments"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"), primary_key=True)

class AuditLog(Base, TenantMixin):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime]
    user_id: Mapped[uuid.UUID | None]
    ip_address: Mapped[str | None]
    user_agent: Mapped[str | None]
    module: Mapped[str]
    action: Mapped[str]                    # CREATE, UPDATE, DELETE, VALIDATE, LOGIN, ...
    object_type: Mapped[str]
    object_id: Mapped[uuid.UUID | None]
    dossier_id: Mapped[uuid.UUID | None]
    data_before: Mapped[dict | None] = mapped_column(JSONB)
    data_after: Mapped[dict | None] = mapped_column(JSONB)
    metadata: Mapped[dict | None] = mapped_column(JSONB)

class Notification(Base, TenantMixin):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str]
    title: Mapped[str]
    message: Mapped[str]
    action_url: Mapped[str | None]
    priority: Mapped[str]                  # "low", "medium", "high"
    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[datetime | None]
    created_at: Mapped[datetime]

class Setting(Base, TenantMixin):
    __tablename__ = "settings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None]
    dossier_id: Mapped[uuid.UUID | None]
    key: Mapped[str]
    value: Mapped[dict] = mapped_column(JSONB)
```

## 13.2 Comptabilité

```python
class Account(Base, TenantMixin, AuditMixin):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    code: Mapped[str]                      # "6111", "34210001"
    label: Mapped[str]
    account_class: Mapped[int]             # 0-9
    account_type: Mapped[str]              # "balance", "income", "off_balance", "analytic", "result"
    normal_balance: Mapped[str]            # "debit", "credit"
    is_collective: Mapped[bool] = mapped_column(default=False)  # Compte collectif (3421, 4411)
    default_tva_code: Mapped[str | None]
    analytic_required: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_system: Mapped[bool] = mapped_column(default=False)  # CGNC base, non modifiable
    parent_code: Mapped[str | None]

class Journal(Base, TenantMixin, AuditMixin):
    __tablename__ = "journals"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    code: Mapped[str]                      # "AC", "VT", "BQ01", "CA", "OD", "PA", "AN"
    label: Mapped[str]
    journal_type: Mapped[str]              # "purchase", "sale", "bank", "cash", "misc", "payroll", "opening"
    default_counterpart_account_id: Mapped[uuid.UUID | None]
    next_sequence: Mapped[int] = mapped_column(default=1)

class JournalEntry(Base, TenantMixin, AuditMixin):
    __tablename__ = "journal_entries"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    journal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journals.id"))
    fiscal_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fiscal_years.id"))
    period_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounting_periods.id"))
    piece_number: Mapped[str | None]       # Attribué à la validation (ex: "AC-2026-000042")
    entry_date: Mapped[date]
    label: Mapped[str]
    reference: Mapped[str | None]          # Numéro facture externe
    status: Mapped[str]                    # "draft", "validated", "reversed", "closed"
    origin: Mapped[str]                    # "manual", "import", "ai", "auto_payroll", "auto_commercial", "auto_tva", "auto_depreciation", "auto_opening"
    source_id: Mapped[uuid.UUID | None]    # ID de l'objet source (facture, bulletin, etc.)
    source_type: Mapped[str | None]        # "invoice", "payslip", "tva_declaration", etc.
    validated_by: Mapped[uuid.UUID | None]
    validated_at: Mapped[datetime | None]
    reversed_by_entry_id: Mapped[uuid.UUID | None]

class JournalEntryLine(Base, TenantMixin):
    __tablename__ = "journal_entry_lines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_entries.id"))
    dossier_id: Mapped[uuid.UUID]          # Denormalized for index performance
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    third_party_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("third_parties.id"))
    label: Mapped[str | None]
    debit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    credit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(default="MAD")
    foreign_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    exchange_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    tva_code: Mapped[str | None]
    tva_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    lettrage_code: Mapped[str | None]      # "AA", "AB", etc.
    lettrage_group_id: Mapped[uuid.UUID | None]
    due_date: Mapped[date | None]
    reconciliation_id: Mapped[uuid.UUID | None]

class ThirdParty(Base, TenantMixin, AuditMixin):
    __tablename__ = "third_parties"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dossiers.id"))
    party_type: Mapped[str]                # "customer", "supplier", "both"
    code: Mapped[str]                      # "CLI001", "FRN001"
    name: Mapped[str]
    ice: Mapped[str | None]
    if_number: Mapped[str | None]
    rc_number: Mapped[str | None]
    address: Mapped[dict | None] = mapped_column(JSONB)
    phone: Mapped[str | None]
    email: Mapped[str | None]
    default_account_id: Mapped[uuid.UUID | None]
    payment_terms_days: Mapped[int | None]
    credit_limit: Mapped[Decimal | None]

class LettrageGroup(Base, TenantMixin):
    __tablename__ = "lettrage_groups"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    account_id: Mapped[uuid.UUID]
    lettrage_code: Mapped[str]
    is_partial: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime]
    created_by: Mapped[uuid.UUID]

class BankReconciliation(Base, TenantMixin, AuditMixin):
    __tablename__ = "bank_reconciliations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    journal_id: Mapped[uuid.UUID]          # Journal de banque
    statement_date: Mapped[date]
    statement_balance: Mapped[Decimal]
    file_document_id: Mapped[uuid.UUID | None]  # Fichier relevé importé
    status: Mapped[str]                    # "in_progress", "completed"

class TVADeclaration(Base, TenantMixin, AuditMixin):
    __tablename__ = "tva_declarations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    period_start: Mapped[date]
    period_end: Mapped[date]
    declaration_type: Mapped[str]          # "monthly", "quarterly"
    tva_collected: Mapped[Decimal]
    tva_deductible_charges: Mapped[Decimal]
    tva_deductible_assets: Mapped[Decimal]
    credit_carried_forward: Mapped[Decimal]
    balance: Mapped[Decimal]               # Positive = due, Negative = credit
    status: Mapped[str]                    # "draft", "calculated", "validated", "filed"
    details: Mapped[dict] = mapped_column(JSONB)  # Breakdown by rate
    validated_by: Mapped[uuid.UUID | None]
    validated_at: Mapped[datetime | None]
    liquidation_entry_id: Mapped[uuid.UUID | None]

class RecurringEntryModel(Base, TenantMixin, AuditMixin):
    __tablename__ = "recurring_entry_models"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    name: Mapped[str]
    journal_id: Mapped[uuid.UUID]
    template_lines: Mapped[list] = mapped_column(JSONB)  # [{account_id, label, debit, credit}]
    frequency: Mapped[str]                 # "monthly", "quarterly", "yearly"
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    next_run_date: Mapped[date]
    is_active: Mapped[bool] = mapped_column(default=True)
```

## 13.3 Paie

```python
class Employee(Base, TenantMixin, AuditMixin):
    __tablename__ = "employees"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"))
    dossier_id: Mapped[uuid.UUID]
    employee_number: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    cin: Mapped[str | None]
    birth_date: Mapped[date | None]
    gender: Mapped[str | None]
    marital_status: Mapped[str | None]     # "single", "married", "divorced", "widowed"
    dependents_count: Mapped[int] = mapped_column(default=0)
    address: Mapped[dict | None] = mapped_column(JSONB)
    phone: Mapped[str | None]
    email: Mapped[str | None]
    bank_rib: Mapped[str | None]
    cnss_number: Mapped[str | None]
    cimr_number: Mapped[str | None]
    mutual_org: Mapped[str | None]
    mutual_number: Mapped[str | None]
    status: Mapped[str]                    # "hired", "active", "suspended", "notice", "departed"
    photo_document_id: Mapped[uuid.UUID | None]

class Contract(Base, TenantMixin, AuditMixin):
    __tablename__ = "contracts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id"))
    contract_type: Mapped[str]             # "cdi", "cdd", "interim", "stage", "anapec"
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    trial_end_date: Mapped[date | None]
    position: Mapped[str]
    category: Mapped[str]                  # "cadre", "employe", "ouvrier"
    base_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    pay_frequency: Mapped[str]             # "monthly", "biweekly", "weekly"
    cimr_employee_rate: Mapped[Decimal | None]
    cimr_employer_rate: Mapped[Decimal | None]
    mutual_employee_rate: Mapped[Decimal | None]
    departure_reason: Mapped[str | None]
    departure_date: Mapped[date | None]

class PayrollPeriod(Base, TenantMixin):
    __tablename__ = "payroll_periods"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    company_id: Mapped[uuid.UUID]
    year: Mapped[int]
    month: Mapped[int]
    status: Mapped[str]                    # "open", "calculated", "verified", "validated"
    validated_by: Mapped[uuid.UUID | None]
    validated_at: Mapped[datetime | None]

class PayrollItem(Base, TenantMixin, AuditMixin):
    __tablename__ = "payroll_items"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID]
    code: Mapped[str]
    label: Mapped[str]
    item_type: Mapped[str]                 # "earning", "deduction", "contribution", "tax"
    nature: Mapped[str]                    # "base", "premium", "overtime", "allowance", "cnss", "cimr", "mutual", "ir"
    formula: Mapped[str | None]            # Expression de calcul
    default_rate: Mapped[Decimal | None]
    is_taxable: Mapped[bool] = mapped_column(default=True)
    is_cnss_subject: Mapped[bool] = mapped_column(default=True)
    calculation_order: Mapped[int]
    is_system: Mapped[bool] = mapped_column(default=False)
    conditions: Mapped[dict | None] = mapped_column(JSONB)  # Conditions d'application

class PayrollRun(Base, TenantMixin, AuditMixin):
    __tablename__ = "payroll_runs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    period_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payroll_periods.id"))
    dossier_id: Mapped[uuid.UUID]
    status: Mapped[str]                    # "pending", "running", "completed", "failed"
    total_gross: Mapped[Decimal | None]
    total_net: Mapped[Decimal | None]
    total_employer_charges: Mapped[Decimal | None]
    employee_count: Mapped[int | None]
    error_log: Mapped[dict | None] = mapped_column(JSONB)
    accounting_entry_id: Mapped[uuid.UUID | None]  # Écriture comptable générée

class Payslip(Base, TenantMixin, AuditMixin):
    __tablename__ = "payslips"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payroll_runs.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id"))
    period_id: Mapped[uuid.UUID]
    dossier_id: Mapped[uuid.UUID]
    gross_salary: Mapped[Decimal]
    gross_taxable: Mapped[Decimal]
    net_taxable: Mapped[Decimal]
    total_employee_deductions: Mapped[Decimal]
    total_employer_charges: Mapped[Decimal]
    ir_amount: Mapped[Decimal]
    net_pay: Mapped[Decimal]
    status: Mapped[str]                    # "draft", "calculated", "validated", "sent"
    pdf_document_id: Mapped[uuid.UUID | None]

class PayslipLine(Base):
    __tablename__ = "payslip_lines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payslip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payslips.id"))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payroll_items.id"))
    label: Mapped[str]
    base: Mapped[Decimal | None]
    rate: Mapped[Decimal | None]
    employee_amount: Mapped[Decimal]
    employer_amount: Mapped[Decimal]
    calculation_order: Mapped[int]

class LeaveRequest(Base, TenantMixin, AuditMixin):
    __tablename__ = "leave_requests"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID]
    leave_type: Mapped[str]                # "annual", "sick", "maternity", "unpaid", "special"
    start_date: Mapped[date]
    end_date: Mapped[date]
    days_count: Mapped[Decimal]
    status: Mapped[str]                    # "requested", "approved", "rejected", "taken", "cancelled"
    approved_by: Mapped[uuid.UUID | None]

class EmployeeLoan(Base, TenantMixin, AuditMixin):
    __tablename__ = "employee_loans"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID]
    amount: Mapped[Decimal]
    interest_rate: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    installments: Mapped[int]
    start_date: Mapped[date]
    remaining_balance: Mapped[Decimal]
    monthly_deduction: Mapped[Decimal]
    status: Mapped[str]                    # "active", "repaying", "settled"

class SocialDeclaration(Base, TenantMixin, AuditMixin):
    __tablename__ = "social_declarations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    declaration_type: Mapped[str]          # "damancom", "9421", "bds"
    period_year: Mapped[int]
    period_month: Mapped[int | None]       # NULL for annual (9421)
    file_document_id: Mapped[uuid.UUID | None]
    status: Mapped[str]                    # "generated", "filed"
    data: Mapped[dict] = mapped_column(JSONB)
```

## 13.4 Commercial

```python
class Customer(Base, TenantMixin, AuditMixin):
    __tablename__ = "customers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    third_party_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("third_parties.id"))
    # Additional commercial fields beyond third_party
    credit_limit: Mapped[Decimal | None]
    payment_terms_days: Mapped[int] = mapped_column(default=30)
    discount_rate: Mapped[Decimal | None]

class Supplier(Base, TenantMixin, AuditMixin):
    __tablename__ = "suppliers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    third_party_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("third_parties.id"))
    payment_terms_days: Mapped[int] = mapped_column(default=30)

class ProductCategory(Base, TenantMixin, AuditMixin):
    __tablename__ = "product_categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    code: Mapped[str]
    label: Mapped[str]
    parent_id: Mapped[uuid.UUID | None]

class Product(Base, TenantMixin, AuditMixin):
    __tablename__ = "products"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    reference: Mapped[str]
    designation: Mapped[str]
    category_id: Mapped[uuid.UUID | None]
    unit: Mapped[str]                      # "unit", "kg", "m", "l", "h"
    purchase_price: Mapped[Decimal | None]
    sale_price_ht: Mapped[Decimal | None]
    tva_code: Mapped[str]                  # "TVA20", "TVA14", "TVA10", "TVA07", "TVA00", "EXON"
    barcode: Mapped[str | None]
    stock_min: Mapped[Decimal | None]
    sale_account_id: Mapped[uuid.UUID | None]    # Compte de vente (711x)
    purchase_account_id: Mapped[uuid.UUID | None] # Compte d'achat (611x)
    stock_account_id: Mapped[uuid.UUID | None]    # Compte de stock (311x)
    is_active: Mapped[bool] = mapped_column(default=True)

class CommercialDocument(Base, TenantMixin, AuditMixin):
    __tablename__ = "commercial_documents"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    document_type: Mapped[str]             # "quotation", "order", "delivery", "invoice", "credit_note"
    document_number: Mapped[str]           # Sequential, e.g. "FAC-2026-000123"
    date: Mapped[date]
    third_party_id: Mapped[uuid.UUID]
    direction: Mapped[str]                 # "sale", "purchase"
    status: Mapped[str]                    # Varies by type (see workflow)
    amount_ht: Mapped[Decimal]
    amount_tva: Mapped[Decimal]
    amount_ttc: Mapped[Decimal]
    currency: Mapped[str] = mapped_column(default="MAD")
    notes: Mapped[str | None]
    parent_document_id: Mapped[uuid.UUID | None]  # Devis → Commande → BL → Facture
    accounting_entry_id: Mapped[uuid.UUID | None]  # Écriture comptable générée
    pdf_document_id: Mapped[uuid.UUID | None]

class CommercialDocumentLine(Base):
    __tablename__ = "commercial_document_lines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commercial_documents.id"))
    product_id: Mapped[uuid.UUID | None]
    designation: Mapped[str]
    quantity: Mapped[Decimal]
    unit_price_ht: Mapped[Decimal]
    discount_percent: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    tva_code: Mapped[str]
    amount_ht: Mapped[Decimal]
    amount_tva: Mapped[Decimal]
    line_order: Mapped[int]

class Payment(Base, TenantMixin, AuditMixin):
    __tablename__ = "payments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    third_party_id: Mapped[uuid.UUID]
    payment_type: Mapped[str]              # "receipt", "disbursement"
    amount: Mapped[Decimal]
    date: Mapped[date]
    payment_method: Mapped[str]            # "cash", "check", "transfer", "card", "bill_of_exchange"
    reference: Mapped[str | None]
    bank_account_id: Mapped[uuid.UUID | None]
    accounting_entry_id: Mapped[uuid.UUID | None]
    status: Mapped[str]                    # "recorded", "reconciled"

class Warehouse(Base, TenantMixin, AuditMixin):
    __tablename__ = "warehouses"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    code: Mapped[str]
    name: Mapped[str]
    address: Mapped[dict | None] = mapped_column(JSONB)
    is_default: Mapped[bool] = mapped_column(default=False)

class StockMovement(Base, TenantMixin, AuditMixin):
    __tablename__ = "stock_movements"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    product_id: Mapped[uuid.UUID]
    warehouse_id: Mapped[uuid.UUID]
    movement_type: Mapped[str]             # "in_reception", "in_adjustment", "out_delivery", "out_adjustment", "transfer"
    quantity: Mapped[Decimal]              # Positive for in, negative for out
    unit_cost: Mapped[Decimal]
    source_document_type: Mapped[str | None]
    source_document_id: Mapped[uuid.UUID | None]
    date: Mapped[date]

class StockLevel(Base, TenantMixin):
    """Materialized/maintained view of current stock per product per warehouse."""
    __tablename__ = "stock_levels"
    product_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    dossier_id: Mapped[uuid.UUID]
    quantity: Mapped[Decimal]
    average_cost: Mapped[Decimal]          # CMUP
    last_updated: Mapped[datetime]
```

## 13.5 Immobilisations

```python
class AssetCategory(Base, TenantMixin):
    __tablename__ = "asset_categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str]
    label: Mapped[str]
    default_duration_years: Mapped[int | None]
    default_method: Mapped[str]            # "linear", "degressive", "none"
    asset_account_code: Mapped[str]        # Classe 2
    depreciation_account_code: Mapped[str] # Classe 28
    expense_account_code: Mapped[str]      # Classe 619
    is_system: Mapped[bool] = mapped_column(default=True)

class FixedAsset(Base, TenantMixin, AuditMixin):
    __tablename__ = "fixed_assets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_categories.id"))
    code: Mapped[str]
    designation: Mapped[str]
    acquisition_date: Mapped[date]
    service_date: Mapped[date]
    original_value: Mapped[Decimal]
    residual_value: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    duration_years: Mapped[int]
    depreciation_method: Mapped[str]       # "linear", "degressive"
    depreciation_rate: Mapped[Decimal]
    supplier_id: Mapped[uuid.UUID | None]
    invoice_reference: Mapped[str | None]
    location: Mapped[str | None]
    inventory_number: Mapped[str | None]
    status: Mapped[str]                    # "active", "fully_depreciated", "disposed", "scrapped"

class DepreciationPlan(Base):
    __tablename__ = "depreciation_plans"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fixed_assets.id"))
    year: Mapped[int]
    opening_nbv: Mapped[Decimal]           # VNC début
    depreciation_amount: Mapped[Decimal]   # Dotation
    cumulative_depreciation: Mapped[Decimal]
    closing_nbv: Mapped[Decimal]           # VNC fin
    is_posted: Mapped[bool] = mapped_column(default=False)
    entry_id: Mapped[uuid.UUID | None]     # Écriture comptable de dotation

class AssetDisposal(Base, TenantMixin, AuditMixin):
    __tablename__ = "asset_disposals"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID]
    disposal_date: Mapped[date]
    disposal_type: Mapped[str]             # "sale", "scrap"
    sale_price: Mapped[Decimal | None]
    nbv_at_disposal: Mapped[Decimal]
    gain_loss: Mapped[Decimal]
    complementary_depreciation: Mapped[Decimal]
    entry_id: Mapped[uuid.UUID | None]
```

## 13.6 Analytique & Budgets

```python
class AnalyticAxis(Base, TenantMixin, AuditMixin):
    __tablename__ = "analytic_axes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    code: Mapped[str]
    label: Mapped[str]
    position: Mapped[int]                  # Ordre d'affichage (1 à 5)
    is_active: Mapped[bool] = mapped_column(default=True)

class AnalyticSection(Base, TenantMixin, AuditMixin):
    __tablename__ = "analytic_sections"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    axis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analytic_axes.id"))
    code: Mapped[str]
    label: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

class AnalyticAllocation(Base):
    __tablename__ = "analytic_allocations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_line_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_entry_lines.id"))
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analytic_sections.id"))
    amount: Mapped[Decimal]
    percentage: Mapped[Decimal]

class AllocationKey(Base, TenantMixin, AuditMixin):
    __tablename__ = "allocation_keys"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    name: Mapped[str]
    account_id: Mapped[uuid.UUID | None]   # Règle par défaut pour un compte
    axis_id: Mapped[uuid.UUID]
    distributions: Mapped[list] = mapped_column(JSONB)  # [{section_id, percentage}]

class Budget(Base, TenantMixin, AuditMixin):
    __tablename__ = "budgets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    fiscal_year_id: Mapped[uuid.UUID]
    name: Mapped[str]
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str]                    # "draft", "approved", "revised"

class BudgetLine(Base):
    __tablename__ = "budget_lines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budgets.id"))
    account_id: Mapped[uuid.UUID]
    section_id: Mapped[uuid.UUID | None]
    month: Mapped[int]
    amount: Mapped[Decimal]
```

## 13.7 Règles & IA

```python
# Rules: voir section 12 (Rule, RuleVersion, RuleDecisionLog)

class DocumentExtraction(Base, TenantMixin):
    __tablename__ = "document_extractions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    extraction_type: Mapped[str]           # "invoice", "bank_statement"
    extracted_fields: Mapped[dict] = mapped_column(JSONB)
    confidence_scores: Mapped[dict] = mapped_column(JSONB)
    model_version: Mapped[str]
    processing_time_ms: Mapped[int | None]
    created_at: Mapped[datetime]

class AISuggestion(Base, TenantMixin):
    __tablename__ = "ai_suggestions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    suggestion_type: Mapped[str]           # "account_imputation", "lettrage", "classification"
    context_type: Mapped[str]              # "journal_entry", "document", "reconciliation"
    context_id: Mapped[uuid.UUID]
    suggested_value: Mapped[dict] = mapped_column(JSONB)
    confidence: Mapped[Decimal]
    status: Mapped[str]                    # "pending", "accepted", "rejected", "ignored"
    accepted_by: Mapped[uuid.UUID | None]
    created_at: Mapped[datetime]

class AnomalyFlag(Base, TenantMixin):
    __tablename__ = "anomaly_flags"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID]
    anomaly_type: Mapped[str]              # "duplicate", "unusual_amount", "unusual_account", "missing_tva", "negative_stock"
    severity: Mapped[str]                  # "info", "warning", "critical"
    object_type: Mapped[str]
    object_id: Mapped[uuid.UUID]
    description: Mapped[str]
    status: Mapped[str]                    # "open", "acknowledged", "resolved", "false_positive"
    resolved_by: Mapped[uuid.UUID | None]
    created_at: Mapped[datetime]
```

---

# 14. Relations principales entre entités

```
Tenant 1──N Company 1──N Dossier 1──N FiscalYear 1──N AccountingPeriod
                                    │
                                    ├──N Account (plan comptable)
                                    ├──N Journal
                                    ├──N JournalEntry 1──N JournalEntryLine
                                    ├──N ThirdParty
                                    │       ├── Customer
                                    │       └── Supplier
                                    ├──N FixedAsset 1──N DepreciationPlan
                                    ├──N AnalyticAxis 1──N AnalyticSection
                                    ├──N Budget 1──N BudgetLine
                                    ├──N TVADeclaration
                                    └──N Document 1──N DocumentLink

Company 1──N Employee 1──N Contract
                        1──N Payslip 1──N PayslipLine
                        1──N LeaveRequest
                        1──N EmployeeLoan

Dossier 1──N PayrollPeriod 1──N PayrollRun 1──N Payslip

Dossier 1──N CommercialDocument 1──N CommercialDocumentLine
        1──N Payment
        1──N Warehouse 1──N StockMovement
        1──N Product

Tenant 1──N User N──N Role (via UserRole)
       1──N Rule 1──N RuleVersion
       1──N AuditLog
       1──N Notification

JournalEntryLine N──1 Account
                 N──1 ThirdParty (optional)
                 N──N AnalyticAllocation N──1 AnalyticSection
```

---

# 15. Stratégie migrations / versioning

## 15.1 Alembic

```bash
# Structure
alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_payroll_tables.py
    ├── 003_add_commercial_tables.py
    └── ...
```

**Convention de nommage** : `{sequence}_{description}.py` (ex: `001_initial_schema.py`).

**Règles** :
- Chaque migration est **réversible** (upgrade + downgrade).
- Les migrations sont revues en code review comme du code applicatif.
- Les migrations destructives (DROP COLUMN, DROP TABLE) nécessitent une approbation explicite.
- En production, les migrations sont exécutées par le pipeline CI/CD, jamais manuellement.
- Les données de seed (plan comptable CGNC, rubriques de paie standard, catégories d'immobilisation) sont livrées dans des migrations dédiées.

## 15.2 Versioning de l'API

- L'API est versionnée dans l'URL : `/api/v1/`, `/api/v2/`.
- Une nouvelle version majeure est créée uniquement en cas de breaking change.
- Les changements non-breaking (ajout de champs, nouveaux endpoints) sont livrés dans la version courante.
- Dépréciation : un endpoint déprécié est maintenu pendant 6 mois minimum avec un header `Deprecation: true`.

---

# 16. Stratégie audit log

## 16.1 Implémentation

```python
# app/core/audit/service.py
class AuditService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def log(
        self,
        action: str,
        object_type: str,
        object_id: uuid.UUID | None = None,
        data_before: dict | None = None,
        data_after: dict | None = None,
        user_id: uuid.UUID | None = None,
        dossier_id: uuid.UUID | None = None,
        metadata: dict | None = None,
    ):
        log_entry = AuditLog(
            tenant_id=get_current_tenant_id(),
            timestamp=datetime.utcnow(),
            user_id=user_id or get_current_user_id(),
            ip_address=get_current_ip(),
            user_agent=get_current_user_agent(),
            module=object_type.split("_")[0] if "_" in object_type else object_type,
            action=action,
            object_type=object_type,
            object_id=object_id,
            dossier_id=dossier_id,
            data_before=data_before,
            data_after=data_after,
            metadata=metadata,
        )
        self.db.add(log_entry)
        # No commit here - will be committed with the main transaction
```

## 16.2 Stockage

La table `audit_logs` est **append-only** et **partitionnée par mois** :

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    -- ... other columns
) PARTITION BY RANGE (timestamp);

CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
-- ... une partition par mois, créées automatiquement
```

**Pas de UPDATE ni DELETE** sur cette table. L'utilisateur PostgreSQL applicatif n'a que le droit `INSERT` et `SELECT` sur `audit_logs`.

---

# 17. Stratégie tests

## 17.1 Pyramide de tests

| Niveau | Outil | Couverture cible | Quoi tester |
|--------|-------|-----------------|-------------|
| **Unit** | pytest | > 90% des services | Logique métier pure (calculs IR, CNSS, équilibre écritures, amortissements) |
| **Integration** | pytest + TestClient + PostgreSQL Docker | > 80% des endpoints | API complète avec base de données réelle |
| **E2E** | Playwright | Flows critiques | Saisie → validation → clôture, calcul paie → bulletin |

## 17.2 Fixtures et factories

```python
# tests/factories.py
import factory
from app.modules.accounting.models import JournalEntry, JournalEntryLine

class TenantFactory(factory.Factory):
    class Meta:
        model = Tenant
    name = factory.Sequence(lambda n: f"Tenant {n}")
    slug = factory.Sequence(lambda n: f"tenant-{n}")
    plan = "pro"
    status = "active"

class DossierFactory(factory.Factory):
    class Meta:
        model = Dossier
    name = factory.Sequence(lambda n: f"Dossier {n}")
    status = "active"

class JournalEntryFactory(factory.Factory):
    class Meta:
        model = JournalEntry
    status = "draft"
    origin = "manual"
    label = "Test entry"
```

## 17.3 Tests critiques (non négociables)

| Test | Module | Description |
|------|--------|-------------|
| `test_entry_must_be_balanced` | Accounting | Vérifier qu'une écriture déséquilibrée est rejetée |
| `test_validated_entry_immutable` | Accounting | Vérifier qu'une écriture validée ne peut pas être modifiée |
| `test_period_lock_prevents_entry` | Closing | Vérifier qu'on ne peut pas saisir dans une période verrouillée |
| `test_ir_calculation_accuracy` | Payroll | Vérifier le calcul IR avec des cas connus (6 tranches du barème) |
| `test_cnss_ceiling` | Payroll | Vérifier le plafond CNSS à 6 000 MAD |
| `test_tva_deductible_delay` | TVA | Vérifier le décalage d'un mois de la TVA déductible |
| `test_depreciation_prorata` | Assets | Vérifier le prorata temporis de première année |
| `test_opening_entries_generation` | Closing | Vérifier la génération des à-nouveaux |
| `test_tenant_isolation` | Core | Vérifier qu'un tenant ne peut pas voir les données d'un autre |
| `test_sequential_numbering` | Accounting | Vérifier la numérotation sans rupture des pièces |

---

# 18. Stratégie observabilité / logs

## 18.1 Stack

| Composant | Outil | Rôle |
|-----------|-------|------|
| **Logs applicatifs** | `structlog` (Python) → stdout → collecte | Logs structurés JSON |
| **Métriques** | Prometheus + Grafana | Temps de réponse, taux d'erreur, queue Celery |
| **Tracing** | OpenTelemetry → Jaeger | Tracing distribué des requêtes |
| **Erreurs** | Sentry | Capture et alerting des exceptions |
| **Health check** | `/health` endpoint | Readiness/liveness pour Docker/K8s |

## 18.2 Format de log structuré

```json
{
  "timestamp": "2026-03-18T14:30:00.123Z",
  "level": "info",
  "logger": "app.modules.accounting.service",
  "message": "Journal entry validated",
  "tenant_id": "uuid",
  "dossier_id": "uuid",
  "user_id": "uuid",
  "entry_id": "uuid",
  "piece_number": "AC-2026-000042",
  "request_id": "uuid",
  "duration_ms": 45
}
```

## 18.3 Métriques clés

| Métrique | Type | Seuil d'alerte |
|----------|------|----------------|
| `http_request_duration_seconds` | Histogram | P95 > 2s |
| `http_requests_total` | Counter | Taux d'erreur 5xx > 1% |
| `celery_task_duration_seconds` | Histogram | Calcul paie > 60s |
| `db_query_duration_seconds` | Histogram | P95 > 500ms |
| `active_users` | Gauge | — |
| `payroll_runs_total` | Counter | — |

---

# 19. Stratégie jobs async

## 19.1 Architecture Celery

```python
# app/celery_app.py
from celery import Celery

celery_app = Celery(
    "easyaccounting",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_time_limit=600,          # 10 min max par tâche
    task_soft_time_limit=540,     # Signal soft à 9 min
    worker_prefetch_multiplier=1, # Fair scheduling
)
```

## 19.2 Tâches asynchrones

| Tâche | Queue | Priorité | Timeout | Description |
|-------|-------|----------|---------|-------------|
| `payroll.compute_run` | `payroll` | Haute | 5 min | Calcul de paie en masse (tous salariés) |
| `reports.generate_pdf` | `reports` | Moyenne | 2 min | Génération PDF (bilan, CPC, balance, bulletin) |
| `reports.generate_edi_xml` | `reports` | Moyenne | 1 min | Génération EDI XML liasse fiscale |
| `documents.ocr_extract` | `ai` | Basse | 2 min | OCR + extraction IA d'un document |
| `imports.process_excel` | `imports` | Moyenne | 5 min | Import Excel d'écritures |
| `imports.process_migration` | `imports` | Basse | 30 min | Migration Atlas/Sage |
| `tva.calculate_declaration` | `accounting` | Moyenne | 2 min | Calcul TVA périodique |
| `assets.calculate_depreciation` | `accounting` | Moyenne | 1 min | Calcul des dotations |
| `closing.generate_opening_entries` | `accounting` | Haute | 5 min | Génération des à-nouveaux |
| `notifications.send_email` | `notifications` | Basse | 30s | Envoi d'email |
| `recurring.generate_entries` | `accounting` | Basse | 1 min | Génération des écritures récurrentes |

## 19.3 Suivi des tâches

```python
# L'API retourne un job_id que le frontend peut poll
@router.post("/payroll/runs", response_model=PayrollRunStarted)
async def start_payroll_run(
    payload: PayrollRunRequest,
    user=Depends(require_permission("payroll", "create")),
):
    task = celery_app.send_task(
        "payroll.compute_run",
        kwargs={"period_id": str(payload.period_id), "tenant_id": str(user.tenant_id)},
        queue="payroll",
    )
    return PayrollRunStarted(job_id=task.id, status="pending")

@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    result = celery_app.AsyncResult(job_id)
    return {
        "job_id": job_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.ready() else None,
        "progress": result.info.get("progress") if result.info else None,
    }
```

---

# 20. Risques techniques majeurs

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RT-01 | **Erreur de calcul comptable/fiscal** : un bug dans le calcul IR, CNSS ou TVA produit des résultats incorrects | Moyenne | Critique | Tests unitaires exhaustifs avec cas réels validés par un expert-comptable. Double-calcul de vérification. Moteur de règles externalisé (données, pas code). |
| RT-02 | **Fuite de données cross-tenant** : une faille dans le RLS expose les données d'un tenant à un autre | Faible | Critique | Tests d'isolation automatisés dans le CI. Audit de sécurité externe. RLS activé au niveau PostgreSQL (pas applicatif uniquement). |
| RT-03 | **Performance dégradée à l'échelle** : lenteur avec 500+ tenants, 100k+ écritures par dossier | Moyenne | Élevé | Indexation agressive, partitioning (audit_logs, journal_entry_lines), cache Redis, pagination obligatoire, benchmark de charge trimestriel. |
| RT-04 | **Perte de données** : crash sans backup, corruption de la base | Faible | Critique | Backup automatique quotidien (pg_dump + WAL archiving). Réplication PostgreSQL. Rétention 30 jours. Test de restauration mensuel. |
| RT-05 | **Migration Atlas échouée** : les données importées depuis Atlas sont incorrectes ou incomplètes | Élevée | Élevé | Tests sur des fichiers Atlas réels. Import en mode "preview" avant validation. Rapport de migration détaillé. Rollback possible. |
| RT-06 | **Montée en charge Celery** : file d'attente saturée pendant les périodes fiscales (janvier-mars) | Moyenne | Moyen | Queues séparées par priorité. Auto-scaling des workers. Monitoring des queues avec alerting. |
| RT-07 | **Précision décimale** : erreurs d'arrondi dans les calculs financiers | Moyenne | Élevé | `Decimal` partout (jamais float). `NUMERIC(15,2)` en base. Tests de précision avec des cas limites. String en JSON pour les montants. |
| RT-08 | **Dépendance au format DGI** : le format EDI XML change et le produit ne génère plus de fichiers valides | Moyenne | Élevé | Veille réglementaire active. XSD validation systématique. Tests de non-régression sur le XML généré. Mise à jour rapide (< 2 semaines). |
| RT-09 | **Complexité du monolithe** : le codebase devient difficile à maintenir avec 14+ modules | Moyenne | Moyen | Architecture modulaire stricte avec frontières claires. Linting des imports inter-modules. Code review systématique. Documentation des interfaces. |
| RT-10 | **Recrutement** : difficulté à trouver des développeurs maîtrisant Python + comptabilité marocaine | Élevée | Élevé | Documentation métier exhaustive (ce PRD + arch fonctionnelle). Onboarding structuré. Formation interne. Partenariat avec un expert-comptable consultant. |

---

# Annexe — docker-compose.yml de développement

```yaml
version: "3.9"

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://ea_user:ea_pass@db:5432/easyaccounting
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=true
    depends_on:
      - db
      - redis
      - minio
    command: uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --reload --factory

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://ea_user:ea_pass@db:5432/easyaccounting
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - db
      - redis
    command: celery -A app.celery_app worker -l info -Q accounting,payroll,reports,ai,imports,notifications

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=easyaccounting
      - POSTGRES_USER=ea_user
      - POSTGRES_PASSWORD=ea_pass
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backend/scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - miniodata:/data
    command: server /data --console-address ":9001"

volumes:
  pgdata:
  miniodata:
```

---

*Ce document constitue l'architecture technique de référence pour EasyAccounting. Il sert de guide pour l'implémentation par l'équipe de développement.*

*Document vivant — à mettre à jour au fil des sprints.*

---

**EasyAccounting** — *Architecture technique d'un ERP pensé pour le Maroc.*
