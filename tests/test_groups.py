import pytest
from httpx import AsyncClient

# =========================================================================
# LIST
# =========================================================================


@pytest.mark.asyncio
async def test_list_groups_empty(client: AsyncClient):
    r = await client.get("/groups/")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_groups_returns_all(client: AsyncClient, seed_groups):
    r = await client.get("/groups/")
    assert r.status_code == 200
    ids = [g["id"] for g in r.json()]
    assert "engineering" in ids
    assert "engineering.backend" in ids
    assert "operations" in ids


@pytest.mark.asyncio
async def test_list_groups_ordered_by_id(client: AsyncClient, seed_groups):
    r = await client.get("/groups/")
    ids = [g["id"] for g in r.json()]
    assert ids == sorted(ids)


# =========================================================================
# GET
# =========================================================================


@pytest.mark.asyncio
async def test_get_group(client: AsyncClient, seed_groups):
    r = await client.get("/groups/engineering.backend")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "engineering.backend"
    assert body["parent_id"] == "engineering"
    assert body["label"] == "Backend"


@pytest.mark.asyncio
async def test_get_group_not_found(client: AsyncClient):
    r = await client.get("/groups/nonexistent")
    assert r.status_code == 404


# =========================================================================
# CREATE
# =========================================================================


@pytest.mark.asyncio
async def test_create_group_top_level(client: AsyncClient):
    r = await client.post(
        "/groups/",
        json={"id": "marketing", "parent_id": None, "label": "Marketing"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == "marketing"
    assert body["parent_id"] is None
    assert body["label"] == "Marketing"


@pytest.mark.asyncio
async def test_create_group_with_parent(client: AsyncClient, seed_groups):
    r = await client.post(
        "/groups/",
        json={
            "id": "engineering.devops",
            "parent_id": "engineering",
            "label": "DevOps",
        },
    )
    assert r.status_code == 201
    assert r.json()["parent_id"] == "engineering"


@pytest.mark.asyncio
async def test_create_group_duplicate_409(client: AsyncClient, seed_groups):
    r = await client.post(
        "/groups/",
        json={"id": "engineering", "parent_id": None, "label": "Duplicate"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_create_group_invalid_parent_422(client: AsyncClient):
    r = await client.post(
        "/groups/",
        json={"id": "child.orphan", "parent_id": "ghost", "label": "Orphan"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_group_empty_id_422(client: AsyncClient):
    r = await client.post(
        "/groups/", json={"id": "", "parent_id": None, "label": "Bad"}
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_group_empty_label_422(client: AsyncClient):
    r = await client.post("/groups/", json={"id": "ok", "parent_id": None, "label": ""})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_group_missing_fields_422(client: AsyncClient):
    r = await client.post("/groups/", json={"id": "only_id"})
    assert r.status_code == 422


# =========================================================================
# PATCH
# =========================================================================


@pytest.mark.asyncio
async def test_update_group_label(client: AsyncClient, seed_groups):
    r = await client.patch("/groups/engineering", json={"label": "Eng"})
    assert r.status_code == 200
    assert r.json()["label"] == "Eng"
    assert r.json()["id"] == "engineering"


@pytest.mark.asyncio
async def test_update_group_parent(client: AsyncClient, seed_groups):
    r = await client.patch(
        "/groups/engineering.backend", json={"parent_id": "operations"}
    )
    assert r.status_code == 200
    assert r.json()["parent_id"] == "operations"


@pytest.mark.asyncio
async def test_update_group_clear_parent(client: AsyncClient, seed_groups):
    r = await client.patch("/groups/engineering.backend", json={"parent_id": None})
    assert r.status_code == 200
    assert r.json()["parent_id"] is None


@pytest.mark.asyncio
async def test_update_group_not_found(client: AsyncClient):
    r = await client.patch("/groups/ghost", json={"label": "X"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_group_invalid_parent_422(client: AsyncClient, seed_groups):
    r = await client.patch(
        "/groups/engineering.backend", json={"parent_id": "nonexistent"}
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_group_noop(client: AsyncClient, seed_groups):
    """PATCH with empty body should succeed and return unchanged data."""
    r = await client.patch("/groups/engineering", json={})
    assert r.status_code == 200
    assert r.json()["label"] == "Engineering"


# =========================================================================
# DELETE
# =========================================================================


@pytest.mark.asyncio
async def test_delete_group(client: AsyncClient, seed_groups):
    r = await client.delete("/groups/engineering.frontend")
    assert r.status_code == 204

    r = await client.get("/groups/engineering.frontend")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_group_not_found(client: AsyncClient):
    r = await client.delete("/groups/nonexistent")
    assert r.status_code == 404
