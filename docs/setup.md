# Setup

## Prerequisites

- **Python 3.11+** with [uv](https://docs.astral.sh/uv/) package manager
- **Node.js 22+** with npm
- **Docker + Docker Compose** (optional, for containerized deployment)
- **CUE CLI** (optional, for automated init) -- [install](https://cuelang.org/docs/install/)
- **GitHub CLI** (optional, for automated init) -- [install](https://cli.github.com/)

## Automated Init (Recommended)

The init script reads `config.cue` and sets up both local `.env` files and GitHub environment secrets/variables in one command.

```bash
# 1. Install dependencies
uv sync

# 2. Copy the config template and fill in your values
cp config.cue.example config.cue
# Edit config.cue with your auth, k8s, and GitHub details

# 3. Authenticate with GitHub
gh auth login

# 4. Preview what will be created
python scripts/init.py --dry-run

# 5. Apply (creates environments, sets secrets/variables, generates .env files)
python scripts/init.py
```

This creates:

- `.env` -- backend environment variables (auth disabled for local dev)
- `frontend/.env` -- frontend Vite environment variables
- GitHub `staging` and `production` environments with all required secrets and variables

To regenerate only the local `.env` files (no GitHub access needed):

```bash
python scripts/init.py --local-only
```

See [Configuration](configuration.md) for the full list of environment variables.

## Manual Setup

If you prefer not to use the init script, configure manually:

### 1. Clone and Configure

```bash
git clone <repository-url>
cd CRUD
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Edit `.env` and `frontend/.env` as needed. The defaults work for local development with auth disabled:

```env
AUTH_DISABLED=true
DATABASE_PATH=./app.db
```

### 2. Start the Backend

```bash
# Install Python dependencies
uv sync

# Start the API server on port 8000
uv run uvicorn app.main:app --reload --port 8000
```

On first launch, the SQLite database file (`app.db`) is created automatically and seeded with example data from `base_data_import/seed.json`.

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server starts on <http://localhost:5173> and proxies API calls (`/groups`, `/items`, `/backup`, `/health`) to `http://localhost:8000`.

### Docker Compose

For a containerized setup:

```bash
docker compose up --build -d
```

This builds a multi-stage Docker image (Node.js for the frontend, Python for the backend), and serves the app at <http://localhost:5173> (host port 5173 mapped to container port 8000). The SQLite database is persisted in a Docker named volume (`app-data`).

To use auth with Docker Compose, configure the build args in `docker-compose.yml` and set the appropriate environment variables in `.env`.

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health
# Should return: {"status":"ok"}

# List groups (auth disabled)
curl http://localhost:8000/groups/
```

## IDE Setup

### VS Code

The repository includes `.vscode/settings.json` with recommended settings. Key configurations:

- Python formatter: Ruff
- Python linter: Ruff
- `pythonPath`: Points to the `.venv` directory

### Recommended Extensions

- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- ESLint (dbaeumer.vscode-eslint)
- Playwright Test (ms-playwright.playwright)
