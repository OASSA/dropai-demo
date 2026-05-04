# DropAI — Intelligent Delivery & Logistics Platform

A production-ready SaaS platform for AI-driven delivery management: shipment tracking, ETA prediction, route optimization, driver assignment, and analytics dashboards.

---

## Architecture Overview

```
dropai/
├── backend/          FastAPI · SQLAlchemy · PostgreSQL · asyncpg
│   ├── app/
│   │   ├── core/     Config, DB engine, JWT security, dependencies
│   │   ├── models/   SQLAlchemy ORM models (9 tables)
│   │   ├── schemas/  Pydantic request/response schemas
│   │   ├── routers/  RESTful API endpoints
│   │   ├── services/ Business logic + AI engine + notifications
│   │   ├── repositories/ Data access layer (repository pattern)
│   │   └── utils/    Logger, audit, helpers
│   ├── config/       apis.yaml — external API configuration
│   └── seed.py       Default data seeder
├── frontend/         React 18 · TypeScript · Tailwind CSS · Vite
│   └── src/
│       ├── pages/    LandingPage, Dashboard, Shipments, Drivers, Warehouses, Analytics…
│       ├── components/ Layout, charts, tables, forms
│       ├── store/    Zustand state management
│       └── services/ Axios API clients
└── docker-compose.yml
```

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env

# 2. Start all services
docker compose up --build

# 3. Seed default data
docker exec dropai_backend python seed.py

# 4. Open the app
# Frontend → http://localhost
# API docs → http://localhost:8000/api/docs
```

---

## Local Development

### Backend

```bash
cd backend

# Create virtualenv
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Set up .env
cp .env.example .env
# Edit DATABASE_URL to point to your local Postgres

# Start server
uvicorn app.main:app --reload --port 8000

# Seed
python seed.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## Default Login

| Role        | Email                | Password  |
|-------------|----------------------|-----------|
| Super Admin | admin@dropai.io      | Admin@123 |

---

## API Documentation

Interactive docs available at:
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Key Endpoints

| Method | Endpoint                          | Description                  |
|--------|-----------------------------------|------------------------------|
| POST   | /api/v1/auth/login                | Authenticate user            |
| GET    | /api/v1/auth/me                   | Current user profile         |
| GET    | /api/v1/companies                 | List companies (super admin) |
| POST   | /api/v1/shipments                 | Create shipment              |
| GET    | /api/v1/shipments/track/{number}  | Public shipment tracking     |
| PUT    | /api/v1/shipments/{id}/assign     | Assign driver                |
| PUT    | /api/v1/shipments/{id}/status     | Update shipment status       |
| GET    | /api/v1/drivers                   | List drivers                 |
| PUT    | /api/v1/drivers/{id}/location     | Update driver GPS            |
| GET    | /api/v1/dashboard/stats           | KPI metrics                  |
| GET    | /api/v1/dashboard/activity        | Audit activity feed          |

---

## User Roles

| Role               | Capabilities                                           |
|--------------------|--------------------------------------------------------|
| **super_admin**    | Full access: all companies, system settings, analytics |
| **company_admin**  | Manage users, view all company shipments               |
| **warehouse_manager** | Create shipments, assign drivers                    |
| **driver**         | View assigned deliveries, update status & location     |
| **customer**       | Track shipment via public tracking page                |

---

## AI Engine

Located in `backend/app/services/ai_service.py`:

- **ETA Prediction** — Heuristic (distance + speed + rush-hour factor). Replace `predict_eta()` with a trained sklearn/PyTorch model.
- **Route Optimization** — Nearest-neighbor heuristic. Replace `optimize_route()` with OR-Tools or Google Routes API.
- **Driver Scoring** — Weighted formula (success rate 60% + rating 40%). Replace `score_driver()` with any ML classifier.

---

## Database Tables

| Table          | Description                                    |
|----------------|------------------------------------------------|
| roles          | System roles with RBAC                         |
| companies      | Multi-tenant company accounts                  |
| users          | Users with role + company association          |
| drivers        | Driver profiles with location + performance    |
| warehouses     | Warehouse locations                            |
| shipments      | Core shipment records with AI fields           |
| tracking_logs  | Status history per shipment                    |
| audit_logs     | Full audit trail (action, old/new values)      |
| notifications  | In-app, email, WhatsApp notifications          |

---

## External Integrations

Configure in `backend/config/apis.yaml` and `backend/.env`:

- **Google Maps** — Distance Matrix + Geocoding (`GOOGLE_MAPS_API_KEY`)
- **WhatsApp** (Twilio) — Delivery notifications (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`)
- **Email** (SendGrid) — Transactional emails (`SENDGRID_API_KEY`)

---

## Environment Variables

See `backend/.env.example` for the full list. Key variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your-64-char-random-secret
GOOGLE_MAPS_API_KEY=
TWILIO_ACCOUNT_SID=
SENDGRID_API_KEY=
```

---

## Production Deployment

The system is containerized and cloud-ready:

- **AWS**: Deploy with ECS Fargate + RDS PostgreSQL + ElastiCache Redis
- **GCP**: Deploy with Cloud Run + Cloud SQL + Memorystore
- Set `DEBUG=false` and use a strong `SECRET_KEY` in production
- Use a managed PostgreSQL (RDS / Cloud SQL) for production databases
- Place a CDN (CloudFront / Cloud CDN) in front of the frontend

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | FastAPI 0.115, SQLAlchemy 2.0, asyncpg          |
| Auth       | JWT (python-jose), bcrypt (passlib)             |
| Database   | PostgreSQL 16                                   |
| Cache      | Redis 7                                         |
| Frontend   | React 18, TypeScript, Vite, Tailwind CSS 3      |
| State      | Zustand                                         |
| Charts     | Recharts                                        |
| HTTP       | Axios                                           |
| Container  | Docker + Docker Compose                         |
