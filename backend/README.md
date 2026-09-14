# 🚀 Utthan FastAPI Backend Service
Phase 2: Backend / API Foundation Layer

The **Utthan Backend Service** provides a secure, server-side API layer between the React citizen-facing frontend and the Supabase PostgreSQL database. It ensures that sensitive database credentials (such as `SUPABASE_SERVICE_ROLE_KEY`) are kept strictly on the server and never exposed to browser clients.

---

## 🏗️ Architecture

```
Citizen Browser (React 19 + Vite 8 SPA)
       │
       │ HTTP / JSON API (CORS Restricted)
       ▼
FastAPI Backend Gateway (Python 3.10+)
       │
       │ Supabase Python SDK / PostgREST
       ▼
Supabase PostgreSQL (Official 36 States, 784 Districts, Schemes, Skills)
```

---

## 📁 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Application entry point, CORS & exception handling
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py             # Environment configuration & settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── supabase.py           # Isolated Supabase client & connection health check
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py             # Health and error schemas
│   │   ├── location.py           # State and district response schemas
│   │   └── opportunity.py        # Opportunity and skill schemas
│   └── api/
│       ├── __init__.py
│       ├── router.py             # Central API router (/api)
│       └── routes/
│           ├── __init__.py
│           ├── health.py         # /api/health and /api/health/db
│           ├── locations.py      # /api/locations/states and state districts
│           └── opportunities.py  # /api/opportunities and opportunity details
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test fixtures & mock Supabase client
│   ├── test_health.py            # Health endpoint tests
│   ├── test_locations.py         # Location endpoint tests
│   └── test_opportunities.py     # Opportunity catalog & filter tests
├── requirements.txt              # Core Python dependencies
├── .env.example                  # Environment template
└── README.md                     # Documentation
```

---

## ⚙️ Environment Configuration

Copy `.env.example` to create your local `.env`:

```bash
cd backend
copy .env.example .env
```

Edit `.env` with your actual Supabase project credentials:

```env
# Supabase Configuration (from Supabase Dashboard -> Project Settings -> API)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Frontend CORS Origin
FRONTEND_ORIGIN=http://localhost:5173

# Server Settings
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

> **Security Note:** Never commit `.env` to Git. The `.gitignore` file is pre-configured to ignore all `.env` files and Python bytecode caches.

---

## 🚀 Running Locally

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be live at:
- **API Root**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive OpenAPI Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoints Reference

### 1. Health Checks
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Basic application heartbeat (no DB required) |
| `GET` | `/api/health/db` | Remote Supabase database connectivity check |

### 2. Locations Master
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/locations/states` | Returns all 36 States/UTs from authoritative master |
| `GET` | `/api/locations/states/{state_code}/districts` | Returns districts for given state (e.g. `UP`, `state-up`) |

### 3. Opportunities Catalog
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/opportunities` | List schemes with optional filters (`state_id`, `category`, `education`, `mobility`) |
| `GET` | `/api/opportunities/{id}` | Detailed opportunity view including mapped NSQF skills |

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:

```bash
cd backend
pytest tests/ -v
```
Tests utilize an in-memory mock client, ensuring tests execute quickly and reliably in CI/CD without requiring live Supabase credentials.
