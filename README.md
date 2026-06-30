  # Compliance Obligations Tracker
  
  Accountability and compliance software for founders: tracking a company's obligations, their due dates, current status, and required documentation. High-stakes domain — the spec demands that a miscalculated date, a leaked sensitive data point, or an unregistered change be impossible.
  
  ## Stack
  
  - **Backend**: FastAPI · Pydantic · SQLAlchemy 2.0 · SQLite (Postgres swappable) · pytest · **56 tests**
  - **Frontend**: Next.js 16 App Router · React 19 · TypeScript strict · Tailwind v4 · Vitest + Testing Library · **13 tests**
  
  ## Structure
  
  ```text
  .
  ├── backend/
  │   ├── domain/             pure entities, state machine, invariants, exceptions
  │   ├── src/
  │   │   ├── api/            FastAPI, routers, error model, log filter
  │   │   ├── models.py       SQLAlchemy 2.0 (Obligation, Audit, Document)
  │   │   ├── repository.py   ObligationRepo, AuditRepo, DocumentRepo (optimistic lock)
  │   │   └── database.py     engine, SessionLocal, init_db(), get_db()
  │   ├── tests/              pytest
  │   ├── init_db.py          creates tables
  │   ├── seed.py             seeds 5 sample obligations
  │   └── requirements.txt
  ├── frontend/
  │   └── src/
  │       ├── app/            layouts, pages, error/loading/not-found
  │       ├── components/     primitives (KpiCard, StatusBadge, ThemeToggle, LocaleSwitch, etc.)
  │       └── lib/            api-client, types, i18n, dictionaries/{es,en}.json
  ├── DECISIONS.md            architecture, decisions and rationale
  ├── pytest.ini              testpaths and pythonpath for pytest
  ├── requirements-dev.txt    pytest, httpx
  └── venv/                   Python venv (not committed)

  ## How to run
  
  ### Backend
  
  ```powershell
  # One time: create venv and install deps
  python -m venv venv
  .\venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r requirements-dev.txt
  
  # Create the DB y place data
  .\venv\Scripts\python.exe backend\init_db.py
  .\venv\Scripts\python.exe backend\seed.py
  
  # Run the API
  $env:PYTHONPATH = "backend"; .\venv\Scripts\python.exe -m uvicorn src.api.main:app
  ```
  
  → Swagger in `http://localhost:8000/docs`
  
  ### Frontend
  
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```
  
  → `http://localhost:3000`
  
  ## How to test
  
  ```powershell
  # Backend (56 tests)
  .\venv\Scripts\python.exe -m pytest
  
  # Frontend (13 tests)
  cd frontend; npm test
  ```
  
  ## Features
  
  - **Dashboard** with KPIs (total, overdue, upcoming, submitted), filtering by status or overdue via URL params, and a table highlighting overdue items.
  - **Detail** with all fields, masked tax ID, history, transitions (the submitted button is disabled if a document is missing), document upload, and loading/error/404 states.
  - **Create / edit** with server-side validation, Server Actions, and revalidation.
  - **i18n** es/en with a header switch (persisted locale cookie, useTransition for smooth refreshing).
  - **Dark mode** with a header switch (localStorage, no incorrect theme flashes).

  ## Endpoints
  
  | Method | Route | Purpose |
  |---|---|---|
  | GET | `/api/obligations` | List (filters: `status`, `overdue`) |
  | GET | `/api/obligations/{id}` | Detail (includes `history`, `documents`, `available_transitions`) |
  | POST | `/api/obligations` | Create |
  | PATCH | `/api/obligations/{id}` | Edit |
  | POST | `/api/obligations/{id}/transitions` | Change state (body: `{to_status, version}`) |
  | POST | `/api/obligations/{id}/documents` | Upload document (multipart) |
  | GET | `/api/obligations/{id}/history` | History only |
  
  Stable error codes in the body {code, message, details?}: NOT_FOUND (404), INVALID_TRANSITION (400), MISSING_DOCUMENT (400), VERSION_CONFLICT (409), VALIDATION_ERROR (422).
  
  ## How to test the doc-gated invariant
  
  1. Create an obligation with requires_document: true.
  2. Transition to in_progress (valid).
  3. Attempt to transition to submitted without uploading a document → the button is disabled on the frontend, and it returns a 400 MISSING_DOCUMENT if forced via the API.
  4. Upload a document, then transition to submitted → succeeds.
