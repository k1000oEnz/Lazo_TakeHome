# Compliance Obligations Tracker

Software de accountability y compliance para founders: qué obligaciones tiene una empresa, cuándo vencen, en qué estado están, con qué documentación. Dominio de alto cuidado — la spec exige que una fecha mal calculada, un dato sensible filtrado o un cambio sin registrar sean imposibles.

## Stack

- **Backend**: FastAPI · Pydantic · SQLAlchemy 2.0 · SQLite (Postgres swappable) · pytest · **56 tests**
- **Frontend**: Next.js 16 App Router · React 19 · TypeScript strict · Tailwind v4 · Vitest + Testing Library · **13 tests**

## Estructura

```
.
├── backend/
│   ├── domain/             entidades puras, state machine, invariantes, excepciones
│   ├── src/
│   │   ├── api/            FastAPI, routers, error model, log filter
│   │   ├── models.py       SQLAlchemy 2.0 (Obligation, Audit, Document)
│   │   ├── repository.py   ObligationRepo, AuditRepo, DocumentRepo (optimistic lock)
│   │   └── database.py     engine, SessionLocal, init_db(), get_db()
│   ├── tests/              pytest
│   ├── init_db.py          crea las tablas
│   ├── seed.py             siembra 5 obligations de muestra
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/            layouts, pages, error/loading/not-found
│       ├── components/     primitivos (KpiCard, StatusBadge, ThemeToggle, LocaleSwitch, etc.)
│       └── lib/            api-client, types, i18n, dictionaries/{es,en}.json
├── DECISIONS.md            arquitectura, decisiones y por qué (leer antes de la defensa)
├── pytest.ini              testpaths y pythonpath para pytest
├── requirements-dev.txt    pytest, httpx
└── venv/                   Python venv (no commiteado)
```

## Cómo correr

### Backend

```powershell
# Una vez: crear venv e instalar deps
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r requirements-dev.txt

# Crear la DB y sembrar datos
.\venv\Scripts\python.exe backend\init_db.py
.\venv\Scripts\python.exe backend\seed.py

# Levantar la API
$env:PYTHONPATH = "backend"; .\venv\Scripts\python.exe -m uvicorn src.api.main:app
```

→ Swagger en `http://localhost:8000/docs`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

→ `http://localhost:3000`

## Cómo testear

```powershell
# Backend (56 tests)
.\venv\Scripts\python.exe -m pytest

# Frontend (13 tests)
cd frontend; npm test
```

## Features

- **Dashboard** con KPIs (total, vencidas, próximas a vencer, presentadas), filtro por status o overdue via URL params, tabla con resalte de vencidas.
- **Detalle** con todos los campos, tax ID enmascarado, historial, transiciones (botón `submitted` bloqueado si falta doc), upload de documentos, estados de loading/error/404.
- **Crear / editar** con validación server-side, Server Actions, revalidación.
- **i18n** es/en con switch en el header (cookie `locale` persistida, `useTransition` para refresh suave).
- **Modo oscuro** con switch en el header (localStorage, sin flash de tema incorrecto).

## Decisiones de diseño

Todo el rationale, las alternativas descartadas y los trade-offs está en [DECISIONS.md](./DECISIONS.md). Puntos clave para la defensa:

- **State machine** como fuente de verdad en `backend/domain/entities.py:ALLOWED_TRANSITIONS`. Transición inválida → 400 `INVALID_TRANSITION`. El front nunca recalcula la state machine: lee `available_transitions` del backend.
- **Doc-gated invariant**: `transition_to()` chequea `requires_document && !has_document` antes de permitir `submitted`. La regla vive en el dominio, no en el handler.
- **Concurrencia**: optimistic lock con columna `version`. `UPDATE ... WHERE id = ? AND version = ?` retorna 0 rows en conflicto → 409 `VERSION_CONFLICT`.
- **Dato sensible** (`company_tax_id`): triple defensa. Entity expone `tax_id_masked`. Pydantic `field_serializer` enmascara en la respuesta. `SensitiveDataFilter` lo strippea de los logs.

## Endpoints

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/api/obligations` | Listar (filtros: `status`, `overdue`) |
| GET | `/api/obligations/{id}` | Detalle (incluye `history`, `documents`, `available_transitions`) |
| POST | `/api/obligations` | Crear |
| PATCH | `/api/obligations/{id}` | Editar |
| POST | `/api/obligations/{id}/transitions` | Cambiar estado (body: `{to_status, version}`) |
| POST | `/api/obligations/{id}/documents` | Subir documento (multipart) |
| GET | `/api/obligations/{id}/history` | Solo historial |

Códigos de error estables en el body `{code, message, details?}`: `NOT_FOUND` (404), `INVALID_TRANSITION` (400), `MISSING_DOCUMENT` (400), `VERSION_CONFLICT` (409), `VALIDATION_ERROR` (422).

## Cómo probar el invariante doc-gated

1. Crear una obligación con `requires_document: true`.
2. Transicionar a `in_progress` (válido).
3. Intentar transicionar a `submitted` sin subir documento → botón deshabilitado en el front, y 400 `MISSING_DOCUMENT` si lo forzás por la API.
4. Subir un documento, después transicionar a `submitted` → funciona.
