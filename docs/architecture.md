# Architecture

## Overview

The CRUD Template application is a full-stack web application with a clear separation between a **generic CRUD framework** (`app/`) and **domain-specific code** (`resources/`). The backend is a FastAPI application with async SQLAlchemy. The frontend is a React 19 SPA that auto-generates CRUD pages from a resource configuration file.

## Repository Structure

```
.
├── app/                        # Generic CRUD framework (reusable across projects)
│   ├── main.py                 # App factory, lifespan, auto-registers routers
│   ├── database.py             # Async SQLAlchemy engine + session factory
│   ├── auth.py                 # Microsoft Entra ID JWT validation
│   ├── models.py               # DeclarativeBase + model re-exports
│   ├── schemas.py              # Schema re-exports for backward compatibility
│   ├── seed.py                 # Backward-compat seed wrapper
│   ├── crud/
│   │   ├── registry.py         # ResourceConfig / ChildResourceConfig dataclasses
│   │   ├── router_factory.py   # Auto-generates CRUD routers from config
│   │   ├── nested_router.py    # Auto-generates nested child routers
│   │   ├── backup.py           # Generic backup/restore router
│   │   └── seed.py             # Generic seed-from-JSON logic
│   ├── routers/                # Empty (legacy; routers are now auto-generated)
│   └── services/               # Application services (empty in template)
│
├── resources/                  # Domain-specific declarations
│   ├── config.py               # Resource registry (single source of truth for backend)
│   ├── models.py               # SQLAlchemy ORM models (Group, Item, Detail)
│   ├── schemas.py              # Pydantic request/response schemas
│   └── routers/                # Custom routers (empty in template)
│
├── frontend/
│   ├── src/
│   │   ├── config/resources.js # Resource registry (single source of truth for frontend)
│   │   ├── api/client.js       # Generic API client + auto-generated CRUD functions
│   │   ├── App.jsx             # Route generation from resource config
│   │   ├── main.jsx            # React entrypoint with AuthProvider
│   │   ├── auth/               # MSAL authentication (Entra ID)
│   │   │   ├── AuthProvider.jsx
│   │   │   ├── RequireAuth.jsx
│   │   │   ├── msalConfig.js
│   │   │   ├── msalInstance.js
│   │   │   └── roles.js
│   │   ├── components/         # Generic CRUD components
│   │   │   ├── CrudList.jsx
│   │   │   ├── CrudCreate.jsx
│   │   │   ├── CrudEdit.jsx
│   │   │   ├── CrudDetail.jsx
│   │   │   ├── CrudForm.jsx
│   │   │   ├── Layout.jsx
│   │   │   ├── ConfirmButton.jsx
│   │   │   ├── ErrorMessage.jsx
│   │   │   └── VersionBar.jsx
│   │   └── pages/              # Page components (can override generic CRUD pages)
│   └── e2e/                    # Playwright end-to-end tests
│
├── tests/                      # Backend pytest suite (async, in-memory SQLite)
├── base_data_import/           # seed.json (seed data)
├── alembic/                    # Database migrations (PostgreSQL only)
├── k8s/                        # Kubernetes manifests (staging/ and production/)
├── .github/                    # GitHub Actions CI workflows
├── .woodpecker/                # Woodpecker CD pipelines
├── Dockerfile                  # Multi-stage build (Node + Python)
└── docker-compose.yml          # Single-service compose with SQLite volume
```

## Generic CRUD Framework

The core design principle is that the `app/` directory contains a reusable CRUD framework that is domain-agnostic. All domain-specific code lives in `resources/`.

### How It Works

1. **Resource Registration**: Domain entities are declared in `resources/config.py` using `ResourceConfig` and `ChildResourceConfig` dataclasses. Each config specifies the model, schemas, primary key type, validation rules, and UI hints.

2. **Auto-Generated Routers**: On startup, `app/main.py` iterates over the resource registry and calls `create_crud_router()` for each resource. This generates LIST, GET, CREATE, UPDATE, and DELETE endpoints automatically.

3. **Nested Resources**: Resources with children (e.g., Items with Details) also get nested routers via `create_nested_crud_router()` for creating, updating, and deleting child records under the parent URL.

4. **Backup/Restore**: A single generic backup router handles serialization and deserialization of all registered resources, including self-referencing FK topological ordering and parent-child inline embedding.

5. **Seeding**: The generic seed module loads initial data from a JSON file that matches the backup format.

### Backend Flow

```
resources/config.py (ResourceRegistry)
        │
        ├── create_crud_router()       → GET/POST/PATCH/DELETE /{resource}/
        ├── create_nested_crud_router() → POST/PATCH/DELETE /{parent}/{pk}/{child}/
        ├── create_backup_router()      → GET /backup/ + POST /backup/restore
        └── _load_custom_routers()      → domain-specific routers (if any)
```

### Frontend Flow

```
config/resources.js
        │
        ├── api/client.js  → auto-generates api.{resource}.list/get/create/update/delete
        └── App.jsx        → auto-generates routes for list/create/detail/edit per resource
                             (with optional page overrides for custom UIs)
```

## Data Model

The template ships with three example entities:

```
GroupModel (PK: string id, dot-notation)
  ├── parent_id → GroupModel (self-referencing hierarchy)
  ├── label: string
  └── details: [DetailModel] (reverse relationship)

ItemModel (PK: auto-increment integer)
  ├── name: string (unique, indexed)
  └── details: [DetailModel] (cascade delete-orphan)

DetailModel (PK: auto-increment integer)
  ├── item_id → ItemModel (FK, CASCADE delete)
  ├── description: text (required)
  ├── notes: text (optional)
  └── group_id → GroupModel (FK)
```

An item can have multiple details, each belonging to a different group.

Groups use a string primary key with dot-notation for hierarchy (e.g., `engineering`, `engineering.backend`, `engineering.frontend`). The `parent_id` field creates a self-referencing tree structure.

## Database

The application supports two database backends:

- **SQLite** (via `aiosqlite`): Used for local development and Docker Compose. Tables are created using `Base.metadata.create_all` on startup.
- **PostgreSQL** (via `asyncpg`): Used in Kubernetes production. Schema is managed via Alembic migrations that run on startup.

Database selection is controlled by environment variables -- see [Configuration](configuration.md).

## Authentication

Authentication uses Microsoft Entra ID (Azure AD):

- **Frontend**: MSAL.js v2 with Authorization Code Flow + PKCE. Tokens stored in memory only. The `AuthProvider` and `RequireAuth` components wrap the entire app.
- **Backend**: JWT validation via PyJWT with JWKS fetched from Microsoft's discovery endpoint. The `require_auth` FastAPI dependency is applied to all generated CRUD routers.
- **RBAC**: App roles (e.g. `App.Admin`, `App.Editor`, `App.Reader`) defined in Entra. The `require_role()` and `require_scope()` dependencies enforce access control.
- **Dev bypass**: Set `AUTH_DISABLED=true` (backend) and `VITE_AUTH_DISABLED=true` (frontend) to skip authentication entirely during local development.

See [Authentication](authentication.md) for full setup instructions.

## Custom Endpoints

The template ships with no custom endpoints. The `resources/routers/` directory is where you add domain-specific endpoints beyond the auto-generated CRUD. See [Development](development.md) for instructions on adding custom endpoints.
