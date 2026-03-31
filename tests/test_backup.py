import pytest
from httpx import AsyncClient

# =========================================================================
# BACKUP (GET /backup/)
# =========================================================================


@pytest.mark.asyncio
async def test_backup_empty_database(client: AsyncClient):
    """Backup of an empty DB returns version and empty arrays."""
    r = await client.get("/backup/")
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == 1
    assert body["groups"] == []
    assert body["items"] == []


@pytest.mark.asyncio
async def test_backup_includes_all_data(client: AsyncClient, seed_item):
    """Backup includes groups, items, and details created by fixtures."""
    r = await client.get("/backup/")
    assert r.status_code == 200
    body = r.json()
    assert len(body["groups"]) == 4  # seed_groups creates 4
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Widget"
    assert len(body["items"][0]["details"]) == 2


@pytest.mark.asyncio
async def test_backup_group_fields(client: AsyncClient, seed_groups):
    """Each backed-up group has id, parent_id, and label."""
    r = await client.get("/backup/")
    groups = {g["id"]: g for g in r.json()["groups"]}
    assert groups["engineering"]["parent_id"] is None
    assert groups["engineering"]["label"] == "Engineering"
    assert groups["engineering.backend"]["parent_id"] == "engineering"


# =========================================================================
# RESTORE (POST /backup/restore)
# =========================================================================


@pytest.mark.asyncio
async def test_restore_replaces_all_data(client: AsyncClient, seed_item):
    """Restore wipes existing data and inserts the new payload."""
    payload = {
        "version": 1,
        "groups": [
            {"id": "finance", "parent_id": None, "label": "Finance"},
        ],
        "items": [
            {
                "name": "Revenue",
                "details": [
                    {
                        "description": "Total revenue metric",
                        "notes": None,
                        "group_id": "finance",
                    }
                ],
            }
        ],
    }
    r = await client.post("/backup/restore", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["groups"] == 1
    assert body["items"] == 1

    # Old data should be gone
    r = await client.get("/groups/engineering")
    assert r.status_code == 404

    # New data should exist
    r = await client.get("/items/")
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Revenue"


@pytest.mark.asyncio
async def test_restore_empty_payload(client: AsyncClient, seed_item):
    """Restoring empty arrays wipes all data."""
    payload = {"version": 1, "groups": [], "items": []}
    r = await client.post("/backup/restore", json=payload)
    assert r.status_code == 200

    r = await client.get("/groups/")
    assert r.json() == []

    r = await client.get("/items/")
    assert r.json() == []


@pytest.mark.asyncio
async def test_restore_with_hierarchical_groups(client: AsyncClient):
    """Restore correctly handles parent-before-child ordering."""
    payload = {
        "version": 1,
        "groups": [
            # Intentionally list child before parent to test topological sort
            {"id": "tech.cloud", "parent_id": "tech", "label": "Cloud"},
            {"id": "tech", "parent_id": None, "label": "Technology"},
        ],
        "items": [],
    }
    r = await client.post("/backup/restore", json=payload)
    assert r.status_code == 200
    assert r.json()["groups"] == 2

    r = await client.get("/groups/tech.cloud")
    assert r.status_code == 200
    assert r.json()["parent_id"] == "tech"


@pytest.mark.asyncio
async def test_backup_roundtrip(client: AsyncClient, seed_item):
    """Export then re-import should produce the same data."""
    # Export
    r = await client.get("/backup/")
    assert r.status_code == 200
    backup_data = r.json()

    # Restore (which wipes and re-creates)
    r = await client.post("/backup/restore", json=backup_data)
    assert r.status_code == 200

    # Export again and compare
    r = await client.get("/backup/")
    restored = r.json()
    assert len(restored["groups"]) == len(backup_data["groups"])
    assert len(restored["items"]) == len(backup_data["items"])
    assert restored["items"][0]["name"] == backup_data["items"][0]["name"]


# =========================================================================
# DELETE GROUP WITH DETAIL FK REFERENCE
# =========================================================================


@pytest.mark.asyncio
async def test_delete_group_used_by_detail(client: AsyncClient, seed_item):
    """Deleting a group referenced by details returns 409."""
    # engineering.backend is used by the seed_item detail
    r = await client.delete("/groups/engineering.backend")
    assert r.status_code == 409
    assert "referenced" in r.json()["detail"].lower()
