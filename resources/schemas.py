"""Application-specific Pydantic request/response schemas.

When creating a new application from the template, replace these schemas
with your own domain-specific validation models.
"""

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------


class GroupCreate(BaseModel):
    id: str = Field(..., min_length=1, examples=["engineering.backend"])
    parent_id: str | None = Field(None, examples=["engineering"])
    label: str = Field(..., min_length=1, examples=["Backend"])


class GroupRead(BaseModel):
    id: str
    parent_id: str | None
    label: str

    model_config = {"from_attributes": True}


class GroupUpdate(BaseModel):
    parent_id: str | None = None
    label: str | None = Field(None, min_length=1)


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------


class DetailCreate(BaseModel):
    description: str = Field(..., min_length=1)
    notes: str | None = Field(None, min_length=1)
    group_id: str = Field(..., min_length=1)


class DetailRead(BaseModel):
    id: int
    description: str
    notes: str | None
    group_id: str

    model_config = {"from_attributes": True}


class DetailUpdate(BaseModel):
    description: str | None = Field(None, min_length=1)
    notes: str | None = None
    group_id: str | None = Field(None, min_length=1)


# ---------------------------------------------------------------------------
# Item
# ---------------------------------------------------------------------------


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    details: list[DetailCreate] = Field(..., min_length=1)


class ItemRead(BaseModel):
    id: int
    name: str
    details: list[DetailRead]

    model_config = {"from_attributes": True}


class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)


# ---------------------------------------------------------------------------
# Backup / Restore  (application-specific backup shapes)
# ---------------------------------------------------------------------------


class BackupDetail(BaseModel):
    description: str
    notes: str | None = None
    group_id: str


class BackupItem(BaseModel):
    name: str
    details: list[BackupDetail]


class BackupGroup(BaseModel):
    id: str
    parent_id: str | None = None
    label: str


class BackupPayload(BaseModel):
    version: int = 1
    groups: list[BackupGroup]
    items: list[BackupItem]
