import pytest
from httpx import AsyncClient

# =========================================================================
# LIST
# =========================================================================


@pytest.mark.asyncio
async def test_list_items_empty(client: AsyncClient):
    r = await client.get("/items/")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_items_returns_all(client: AsyncClient, seed_item):
    r = await client.get("/items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    names = [i["name"] for i in items]
    assert "Widget" in names


@pytest.mark.asyncio
async def test_list_items_search(client: AsyncClient, seed_item):
    r = await client.get("/items/?q=Widget")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Widget"


@pytest.mark.asyncio
async def test_list_items_search_no_match(client: AsyncClient, seed_item):
    r = await client.get("/items/?q=nonexistent")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_items_filter_by_group(client: AsyncClient, seed_item):
    r = await client.get("/items/?group=engineering.backend")
    assert r.status_code == 200
    assert len(r.json()) >= 1


# =========================================================================
# GET
# =========================================================================


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.get(f"/items/{item_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == item_id
    assert body["name"] == "Widget"
    assert len(body["details"]) == 2


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient):
    r = await client.get("/items/99999")
    assert r.status_code == 404


# =========================================================================
# CREATE
# =========================================================================


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, seed_groups):
    r = await client.post(
        "/items/",
        json={
            "name": "Gadget",
            "details": [
                {
                    "description": "A useful gadget",
                    "notes": "Version 1",
                    "group_id": "engineering",
                }
            ],
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Gadget"
    assert len(body["details"]) == 1
    assert body["details"][0]["description"] == "A useful gadget"
    assert body["details"][0]["notes"] == "Version 1"
    assert body["details"][0]["group_id"] == "engineering"


@pytest.mark.asyncio
async def test_create_item_duplicate_409(client: AsyncClient, seed_item):
    r = await client.post(
        "/items/",
        json={
            "name": "Widget",
            "details": [
                {
                    "description": "Duplicate",
                    "group_id": "engineering",
                }
            ],
        },
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_create_item_invalid_group_422(client: AsyncClient, seed_groups):
    r = await client.post(
        "/items/",
        json={
            "name": "Bad Item",
            "details": [
                {
                    "description": "Bad ref",
                    "group_id": "nonexistent",
                }
            ],
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_item_empty_name_422(client: AsyncClient, seed_groups):
    r = await client.post(
        "/items/",
        json={
            "name": "",
            "details": [{"description": "Something", "group_id": "engineering"}],
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_item_no_details_422(client: AsyncClient, seed_groups):
    r = await client.post("/items/", json={"name": "Lonely"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_item_empty_details_422(client: AsyncClient, seed_groups):
    r = await client.post("/items/", json={"name": "Lonely", "details": []})
    assert r.status_code == 422


# =========================================================================
# PATCH
# =========================================================================


@pytest.mark.asyncio
async def test_update_item_name(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.patch(f"/items/{item_id}", json={"name": "Super Widget"})
    assert r.status_code == 200
    assert r.json()["name"] == "Super Widget"


@pytest.mark.asyncio
async def test_update_item_duplicate_name_409(client: AsyncClient, seed_item):
    # Create a second item
    r = await client.post(
        "/items/",
        json={
            "name": "Gadget",
            "details": [{"description": "A gadget", "group_id": "engineering"}],
        },
    )
    assert r.status_code == 201
    second_id = r.json()["id"]

    # Try to rename second item to same name as first
    r = await client.patch(f"/items/{second_id}", json={"name": "Widget"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_update_item_not_found(client: AsyncClient):
    r = await client.patch("/items/99999", json={"name": "Ghost"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_item_noop(client: AsyncClient, seed_item):
    """PATCH with empty body should succeed and return unchanged data."""
    item_id = seed_item["id"]
    r = await client.patch(f"/items/{item_id}", json={})
    assert r.status_code == 200
    assert r.json()["name"] == "Widget"


# =========================================================================
# DELETE
# =========================================================================


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.delete(f"/items/{item_id}")
    assert r.status_code == 204

    r = await client.get(f"/items/{item_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_item_not_found(client: AsyncClient):
    r = await client.delete("/items/99999")
    assert r.status_code == 404
