# CRUD Template

A full-stack generic CRUD application template. Define your entities in configuration files and the framework auto-generates backend routers, API client functions, and frontend pages.

## Features

- **Auto-generated CRUD** -- declare resources in config and get full create, read, update, delete endpoints and UI pages
- **Hierarchical groups** -- dot-notation taxonomy (e.g. `engineering.backend`) with parent-child relationships
- **Nested resources** -- items with child details, managed through parent routes
- **Search and filter** -- real-time text search with group dropdown filter
- **Backup and restore** -- download the entire database as JSON or upload a JSON file to restore it
- **Microsoft Entra ID authentication** -- OIDC + OAuth 2.0 with PKCE, RBAC roles, and JWT validation
- **Seed data** -- ships with example groups and items for quick start

## Tech Stack

| Layer      | Technology                                               |
|------------|----------------------------------------------------------|
| Backend    | Python 3.11+, FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Database   | SQLite (local dev / Docker) or PostgreSQL (production)   |
| Frontend   | React 19, React Router 7, Vite 8                        |
| Auth       | Microsoft Entra ID (MSAL.js + PyJWT)                    |
| Testing    | pytest, Vitest, Playwright                               |
| Packaging  | uv (Python), npm (Node)                                  |
| Container  | Docker (multi-stage, multi-platform) + Docker Compose    |
| CI/CD      | GitHub Actions                                           |
| Deployment | Kubernetes (k3s) with Traefik + CloudNativePG            |

## Quick Start

### Prerequisites

- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22+ with npm

### Backend

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

The database is created automatically on first launch and seeded with example data.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server proxies API calls to port 8000.

### Docker

```bash
docker compose up --build -d
```

The app is served at <http://localhost:5173> (mapped from container port 8000). The SQLite database is persisted in a Docker named volume.

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, generic CRUD framework, data model |
| [Setup](docs/setup.md) | Installation and local development |
| [Configuration](docs/configuration.md) | Environment variables reference |
| [API](docs/api.md) | REST API endpoints and data model |
| [Authentication](docs/authentication.md) | Microsoft Entra ID setup and auth flows |
| [Development](docs/development.md) | Coding conventions, adding entities, linting |
| [Testing](docs/testing.md) | Backend, frontend unit, and E2E testing |
| [Deployment](docs/deployment.md) | Docker, Kubernetes, CI/CD pipelines |

## License

Internal project -- see repository access settings.
