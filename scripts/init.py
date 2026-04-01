"""Bootstrap GitHub environments, secrets, and variables from config.cue.

Also generates local .env files for development.

Prerequisites:
    - cue CLI  (https://cuelang.org/docs/install/)
    - gh CLI   (https://cli.github.com/) authenticated via ``gh auth login``

Usage:
    python scripts/init.py              # apply changes
    python scripts/init.py --dry-run    # preview without making changes
    python scripts/init.py --local-only # only generate .env files, skip GitHub
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.cue"
CONFIG_EXAMPLE = PROJECT_ROOT / "config.cue.example"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_tool(name: str, *, hint: str) -> None:
    """Abort if a required CLI tool is not on PATH."""
    if shutil.which(name) is None:
        logger.error("%s not found on PATH. %s", name, hint)
        sys.exit(1)


def _run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a subprocess, returning its result."""
    logger.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _load_config() -> dict:
    """Export config.cue as JSON via the cue CLI."""
    if not CONFIG_FILE.exists():
        logger.error(
            "config.cue not found at %s\n"
            "Copy the example and fill in your values:\n"
            "  cp config.cue.example config.cue",
            CONFIG_FILE,
        )
        sys.exit(1)

    result = _run(["cue", "export", str(CONFIG_FILE), "--out", "json"])
    if result.returncode != 0:
        logger.error("cue export failed:\n%s", result.stderr.strip())
        sys.exit(1)

    return json.loads(result.stdout)


def _check_gh_auth() -> None:
    """Verify the user is authenticated with the gh CLI."""
    result = _run(["gh", "auth", "status"], check=False)
    if result.returncode != 0:
        logger.error("Not authenticated with GitHub CLI.\nRun: gh auth login")
        sys.exit(1)


# ---------------------------------------------------------------------------
# GitHub operations
# ---------------------------------------------------------------------------


def _ensure_environment(repo: str, env_name: str, *, dry_run: bool) -> None:
    """Create a GitHub deployment environment (idempotent)."""
    if dry_run:
        logger.info("[dry-run] Would create environment: %s", env_name)
        return
    result = _run(
        [
            "gh",
            "api",
            "--method",
            "PUT",
            f"repos/{repo}/environments/{env_name}",
        ],
        check=False,
    )
    if result.returncode != 0:
        logger.error(
            "Failed to create environment %s:\n%s",
            env_name,
            result.stderr.strip(),
        )
        sys.exit(1)
    logger.info("Environment created/verified: %s", env_name)


def _set_secret(
    repo: str, env_name: str, name: str, value: str, *, dry_run: bool
) -> None:
    """Set a GitHub Actions environment secret."""
    if dry_run:
        logger.info("[dry-run] Would set secret  %s/%s", env_name, name)
        return
    result = _run(
        [
            "gh",
            "secret",
            "set",
            name,
            "--env",
            env_name,
            "--body",
            value,
            "-R",
            repo,
        ],
        check=False,
    )
    if result.returncode != 0:
        logger.error(
            "Failed to set secret %s/%s:\n%s",
            env_name,
            name,
            result.stderr.strip(),
        )
        sys.exit(1)
    logger.info("Secret set: %s/%s", env_name, name)


def _set_variable(
    repo: str, env_name: str, name: str, value: str, *, dry_run: bool
) -> None:
    """Set a GitHub Actions environment variable (create or update)."""
    if dry_run:
        logger.info("[dry-run] Would set variable %s/%s = %s", env_name, name, value)
        return
    # Try to set (create). If it already exists, gh returns non-zero.
    result = _run(
        [
            "gh",
            "variable",
            "set",
            name,
            "--env",
            env_name,
            "--body",
            value,
            "-R",
            repo,
        ],
        check=False,
    )
    if result.returncode != 0:
        logger.error(
            "Failed to set variable %s/%s:\n%s",
            env_name,
            name,
            result.stderr.strip(),
        )
        sys.exit(1)
    logger.info("Variable set: %s/%s = %s", env_name, name, value)


def _push_to_github(config: dict, *, dry_run: bool) -> None:
    """Push all environments, secrets, and variables to GitHub."""
    gh = config["github"]
    repo = f"{gh['organization']}/{gh['repository']}"
    environments = gh.get("environment", {})

    if not environments:
        logger.warning("No environments defined in config.cue — nothing to push.")
        return

    logger.info("Target repository: %s", repo)
    logger.info("Environments: %s", ", ".join(environments))
    logger.info("")

    for env_name, env_cfg in environments.items():
        logger.info("── %s ──", env_name)
        _ensure_environment(repo, env_name, dry_run=dry_run)

        for secret_name, secret_value in env_cfg.get("secrets", {}).items():
            _set_secret(repo, env_name, secret_name, secret_value, dry_run=dry_run)

        for var_name, var_value in env_cfg.get("variables", {}).items():
            _set_variable(repo, env_name, var_name, var_value, dry_run=dry_run)

        logger.info("")


# ---------------------------------------------------------------------------
# Local .env generation
# ---------------------------------------------------------------------------


def _generate_env_files(config: dict, *, dry_run: bool) -> None:
    """Generate .env and frontend/.env from config.cue values."""
    auth = config.get("auth", {})

    # --- Backend .env ---
    backend_env = PROJECT_ROOT / ".env"
    backend_lines = [
        "# Generated by scripts/init.py from config.cue",
        "# Re-run `python scripts/init.py` to regenerate.",
        "",
        "# ── Microsoft Entra ID Authentication ──",
        "AUTH_DISABLED=true",
        f"TENANT_ID={auth.get('TENANT_ID', '')}",
        f"API_AUDIENCE={auth.get('API_AUDIENCE', '')}",
        "",
        "# ── CORS ──",
        "CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000",
        "",
        "# ── Database ──",
        "DATABASE_PATH=./app.db",
    ]
    backend_content = "\n".join(backend_lines) + "\n"

    if dry_run:
        logger.info("[dry-run] Would write %s:\n%s", backend_env, backend_content)
    else:
        backend_env.write_text(backend_content)
        logger.info("Generated %s", backend_env)

    # --- Frontend .env ---
    frontend_env = PROJECT_ROOT / "frontend" / ".env"
    frontend_lines = [
        "# Generated by scripts/init.py from config.cue",
        "# Re-run `python scripts/init.py` to regenerate.",
        "",
        f"VITE_CLIENT_ID={auth.get('SPA_CLIENT_ID', '')}",
        f"VITE_TENANT_ID={auth.get('TENANT_ID', '')}",
        f"VITE_API_SCOPE={auth.get('API_SCOPE', '')}",
        f"VITE_AUTHORITY={auth.get('AUTHORITY', '')}",
        "",
        "# Set to true to bypass MSAL for local development",
        "VITE_AUTH_DISABLED=true",
    ]
    frontend_content = "\n".join(frontend_lines) + "\n"

    if dry_run:
        logger.info("[dry-run] Would write %s:\n%s", frontend_env, frontend_content)
    else:
        frontend_env.write_text(frontend_content)
        logger.info("Generated %s", frontend_env)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap GitHub environments and local .env files from config.cue",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Only generate local .env files, skip GitHub setup",
    )
    args = parser.parse_args()

    # Prerequisites
    _check_tool("cue", hint="Install from https://cuelang.org/docs/install/")
    if not args.local_only:
        _check_tool("gh", hint="Install from https://cli.github.com/")
        _check_gh_auth()

    # Load config
    config = _load_config()

    # Generate local .env files
    logger.info("── Generating local .env files ──")
    _generate_env_files(config, dry_run=args.dry_run)
    logger.info("")

    # Push to GitHub
    if not args.local_only:
        logger.info("── Pushing to GitHub ──")
        _push_to_github(config, dry_run=args.dry_run)

    if args.dry_run:
        logger.info("Dry run complete. No changes were made.")
    else:
        logger.info("Done.")


if __name__ == "__main__":
    main()
