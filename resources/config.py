"""Application resource configuration — the single source of truth.

This file registers all CRUD resources with the generic framework.
When creating a new application, modify this file to define your
domain entities and their relationships.
"""

from __future__ import annotations

from pathlib import Path

from app.crud.registry import ChildResourceConfig, ResourceConfig, ResourceRegistry
from resources.models import DetailModel, GroupModel, ItemModel
from resources.schemas import (
    BackupGroup,
    BackupItem,
    DetailCreate,
    DetailRead,
    DetailUpdate,
    GroupCreate,
    GroupRead,
    GroupUpdate,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------

APP_TITLE = "CRUD API"
APP_VERSION = "0.1.0"

# Role required for destructive operations (backup restore)
ADMIN_ROLE = "App.Admin"

# Seed data file
SEED_FILE = Path(__file__).resolve().parent.parent / "base_data_import" / "seed.json"

# ---------------------------------------------------------------------------
# Resource definitions
# ---------------------------------------------------------------------------

registry = ResourceRegistry()

# -- Groups (self-referencing hierarchy) ------------------------------------

registry.register(
    ResourceConfig(
        name="groups",
        model=GroupModel,
        create_schema=GroupCreate,
        read_schema=GroupRead,
        update_schema=GroupUpdate,
        pk_field="id",
        pk_type=str,
        order_by="id",
        unique_fields=["id"],
        fk_validations={"parent_id": GroupModel},
        protect_on_delete=True,
        label="Groups",
        label_singular="Group",
        backup_schema=BackupGroup,
        self_referencing_fk="parent_id",
    )
)

# -- Items (with nested details) -------------------------------------------

registry.register(
    ResourceConfig(
        name="items",
        model=ItemModel,
        create_schema=ItemCreate,
        read_schema=ItemRead,
        update_schema=ItemUpdate,
        pk_field="id",
        pk_type=int,
        order_by="name",
        unique_fields=["name"],
        searchable_fields=["name"],
        filterable_fks={"group": "details.group_id"},
        label="Items",
        label_singular="Item",
        backup_schema=BackupItem,
        backup_children_field="details",
        children=[
            ChildResourceConfig(
                name="details",
                model=DetailModel,
                create_schema=DetailCreate,
                read_schema=DetailRead,
                update_schema=DetailUpdate,
                pk_field="id",
                pk_type=int,
                parent_fk="item_id",
                fk_validations={"group_id": GroupModel},
                label="Details",
                label_singular="Detail",
            )
        ],
    )
)

# ---------------------------------------------------------------------------
# Custom routers (domain-specific endpoints beyond generic CRUD)
# ---------------------------------------------------------------------------

# Import custom routers lazily to avoid circular imports.  Each custom
# router is a standard FastAPI APIRouter.
CUSTOM_ROUTERS: list = []


def _load_custom_routers():
    """Load application-specific routers that aren't auto-generated."""
    return []
