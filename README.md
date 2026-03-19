# EasyAccounting

ERP SaaS marocain unifié — Comptabilité · Paie · Commercial · Fiscalité · IA

## Stack technique

| Couche | Technologies |
|--------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL 16 |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query, Zod |
| Infra | Docker, docker-compose, Redis, MinIO |

## Lancement rapide

### Prérequis

- Docker et docker-compose installés
- Ports 3000, 5432, 6379, 8000, 9000, 9001 disponibles

### 1. Lancer les services

```bash
docker-compose up --build
```

### 2. Créer les tables (première fois)

```bash
docker-compose exec api alembic upgrade head
```

Si aucune migration n'existe encore, générer la migration initiale :

```bash
docker-compose exec api alembic revision --autogenerate -m "initial"
docker-compose exec api alembic upgrade head
```

### 3. Accéder à l'application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/docs |
| API docs (ReDoc) | http://localhost:8000/redoc |
| MinIO Console | http://localhost:9001 |

### 4. Créer un compte

Via le frontend (page de login) ou via l'API :

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "MonMotDePasse123",
    "first_name": "Admin",
    "last_name": "EasyAccounting",
    "company_name": "Ma Fiduciaire"
  }'
```

## Structure du projet

```
EasyAccounting/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── auth/           # Authentification, JWT, RBAC
│   │   ├── tenant/         # Tenants, sociétés, dossiers
│   │   ├── core/           # Exercices, périodes, audit, documents
│   │   ├── accounting/     # Plan comptable, journaux, écritures
│   │   ├── shared/         # Base models, exceptions, event bus
│   │   └── middleware/     # Tenant RLS injection
│   ├── alembic/            # Migrations DB
│   └── tests/              # Tests pytest
├── frontend/               # Next.js App
│   └── src/
│       ├── app/            # Pages (App Router)
│       ├── components/     # UI components
│       ├── hooks/          # React hooks
│       ├── lib/            # API client, auth, utils
│       └── types/          # TypeScript types
├── scripts/                # Init scripts
└── docker-compose.yml
```

## Développement

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | /api/v1/auth/register | Inscription |
| POST | /api/v1/auth/login | Connexion |
| GET | /api/v1/auth/me | Utilisateur courant |
| GET | /api/v1/tenant/companies | Liste des sociétés |
| POST | /api/v1/tenant/companies | Créer une société |
| GET | /api/v1/tenant/dossiers | Liste des dossiers |
| POST | /api/v1/tenant/dossiers | Créer un dossier |
| GET | /api/v1/core/fiscal-years | Liste exercices |
| POST | /api/v1/core/fiscal-years | Créer un exercice |
| POST | /api/v1/core/periods/{id}/lock | Verrouiller une période |
| GET | /api/v1/core/audit-logs | Logs d'audit |
| GET | /api/v1/accounting/accounts | Plan de comptes |
| POST | /api/v1/accounting/accounts | Créer un compte |
| GET | /api/v1/accounting/journals | Liste des journaux |
| POST | /api/v1/accounting/journals | Créer un journal |
| GET | /api/v1/accounting/entries | Liste des écritures |
| POST | /api/v1/accounting/entries | Créer une écriture |
| POST | /api/v1/accounting/entries/{id}/validate | Valider une écriture |
| POST | /api/v1/accounting/entries/{id}/reverse | Contrepasser |
| GET | /api/v1/health | Healthcheck |
