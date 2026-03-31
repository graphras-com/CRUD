"""Pydantic schema re-exports for backward compatibility.

Concrete schemas are defined in :mod:`resources.schemas`.  This module
re-exports them so that existing imports (``from app.schemas import ...``)
continue to work without changes.
"""

from resources.schemas import (  # noqa: F401
    BackupDetail,
    BackupGroup,
    BackupItem,
    BackupPayload,
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
