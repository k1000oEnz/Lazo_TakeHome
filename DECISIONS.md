# DECISIONS

## 1. Backend Architecture

Layers, from the inside out:

- `domain/` — pure entities, state machine, invariants, exceptions. No imports from FastAPI, Pydantic, SQLAlchemy, or IO stdlib. The "cannot transition to `submitted` without a document" rule lives here. If tomorrow we swap SQLite for Postgres, this directory remains untouched.
- `src/repository.py` — the only layer that talks to SQLAlchemy. Returns and accepts entities from `domain/`, not ORM models.
- `src/service.py` — orchestrator. Receives the entity from the repo, applies the transition (which is a method on the entity), and delegates persistence to the repo. Catches `DomainError` solely for logging and metrics. The HTTP mapping is handled by the handler.
- Routers in `src/api/` — the only layer that imports `fastapi`. Validates input with Pydantic, calls the service, maps errors to HTTP.

### Discarded Alternatives

- **State machine in Pydantic with `field_validator`**: rejected. Pydantic validates shape, not business rules. Furthermore, any import of the module drags in dependencies that the domain shouldn't know about.
- **State machine in `models.py` (ORM-driven)**: rejected. Couples the rule to the table. If tomorrow the domain needs to run from a script or a batch job without a DB, it cannot.
- **SQLAlchemy events for invariants**: rejected. The doc-gated invariant must fail before touching the DB, not in a post-flush hook.

## 2. Frontend Architecture

- **Server Components by default**. Client Components only where there is state (filters, modals, forms, transition buttons).
- **Server Actions** for mutations. `revalidatePath` after each mutation so the detail server component refreshes without polling.
- No Redux or Zustand. Local state with `useState` for filters and `useFormStatus` for forms. A global store is not justified for this domain.
- Layers:
  - `app/` — routes, server components, layouts.
  - `components/` — primitive, atomic UI, no business logic.
  - `features/` — UI compositions with feature logic.
  - `lib/` — API client, i18n, shared types.

### i18n

- `next-intl` with two dictionaries: `messages/en.json` and `messages/es.json`.
- Product strings in the dictionaries, not hardcoded.
- Backend error messages arrive with a stable `code` (e.g., `MISSING_DOCUMENT`). The client maps `code` → i18n string; it never translates the backend's `message`.

## 3. API Contract

| Method | Path | Body | Response | Errors |
|---|---|---|---|---|
| GET | `/api/obligations` | — (query: `status`, `type`, `q`, `overdue`) | `200 List<ObligationSummary>` | 422 |
| GET | `/api/obligations/{id}` | — | `200 ObligationDetail` (with `history` and `available_transitions`) | 404 |
| POST | `/api/obligations` | `ObligationCreate` | `201 ObligationDetail` | 422 |
| PATCH | `/api/obligations/{id}` | `ObligationUpdate` | `200 ObligationDetail` | 404, 422 |
| POST | `/api/obligations/{id}/transitions` | `{to_status, version, document_id?}` | `200 ObligationDetail` | 400 `INVALID_TRANSITION`, 400 `MISSING_DOCUMENT`, 404, 409 `VERSION_CONFLICT` |
| POST | `/api/obligations/{id}/documents` | multipart | `201 {document_id, filename, size}` | 404 |
| GET | `/api/obligations/{id}/history` | — | `200 List<HistoryEntry>` | 404 |

### Consistent Error Model

```json
{
  "code": "MISSING_DOCUMENT",
  "message": "Document required to mark as submitted",
  "details": { "requires_document": true }
}

```

Stable codes. The frontend uses them as i18n keys and does not translate the `message`.

## 4. Concurrency

**Decision**: optimistic locking with a `version` column (monotonic integer).

**How it works**:

1. `SELECT ... WHERE id = ?` → returns `version = N`.
2. The client decides `to_status = X` and sends `version: N` in the body.
3. `UPDATE ... SET status = X, version = N+1 WHERE id = ? AND version = N`.
4. If `rows_affected == 0`, another request wrote in between → 409 `VERSION_CONFLICT`.
5. The client re-fetches and decides again.

## 5. Sensitive Data (`company_tax_id`)

**How it is handled**:

* **Saved completely** in the column. Necessary for real reporting. Not hashed because the domain (EIN/Tax ID) has a small search space and is reversible using rainbow tables.
* **Displayed masked** in every API response. The domain entity exposes `tax_id_masked` as a property; the response schema uses a `field_serializer` that formats it as `****-1234`. Double defense: the entity never returns the raw value to the handler.
* **Never logged**. The project logger has a registered `Filter` that omits any field named `company_tax_id` or `tax_id` in `extra={}`. Furthermore, the service neither receives nor logs the field: it only operates on the entity.
* **Never travels in the query string or path**. Only in the body of POST and PATCH requests.

## 7. AI Usage

Tool: AI assistant (claudecode) in pair-programmer mode.

**Where it helped**:

* Helped mainly within the backend, where I had less experience; I started brainstorming ideas and solidifying them with the use of AI.
* Structuring the backend, such as folder division and creating a **requirements.txt** file to install the necessary libraries.
* Also with writing tests for both the frontend and backend.

**Where I corrected it**:

* Suggested `Decimal` for `due_date`. **Rejected**: it's a date, not money. `date` from `datetime` is the correct approach.
* Modified **models.py** because the repository was showing a false positive for errors; to avoid silencing the error, I updated the syntax to SQLAlchemy 2.0.

**Where I rejected it**:

* Proposed adding JWT authentication from the beginning. **Rejected**: the prompt doesn't ask for it, and real auth is a rabbit hole that distracts from the core domain being evaluated.
