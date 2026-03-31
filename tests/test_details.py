import pytest
from httpx import AsyncClient

# =========================================================================
# ADD DETAIL
# =========================================================================


@pytest.mark.asyncio
async def test_add_detail(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.post(
        f"/items/{item_id}/details",
        json={
            "description": "Third detail entry",
            "notes": "Extra notes",
            "group_id": "operations",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["description"] == "Third detail entry"
    assert body["notes"] == "Extra notes"
    assert body["group_id"] == "operations"
    assert body["id"] is not None

    # Verify it appears on the item
    r = await client.get(f"/items/{item_id}")
    assert len(r.json()["details"]) == 3


@pytest.mark.asyncio
async def test_add_detail_without_notes(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.post(
        f"/items/{item_id}/details",
        json={"description": "Description only", "group_id": "engineering"},
    )
    assert r.status_code == 201
    assert r.json()["notes"] is None


@pytest.mark.asyncio
async def test_add_detail_item_not_found(client: AsyncClient, seed_groups):
    r = await client.post(
        "/items/99999/details",
        json={"description": "Orphan", "group_id": "engineering"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_add_detail_invalid_group_422(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.post(
        f"/items/{item_id}/details",
        json={"description": "Bad ref", "group_id": "ghost"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_add_detail_empty_description_422(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.post(
        f"/items/{item_id}/details",
        json={"description": "", "group_id": "engineering"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_add_detail_missing_fields_422(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.post(f"/items/{item_id}/details", json={"description": "No group"})
    assert r.status_code == 422


# =========================================================================
# PATCH DETAIL
# =========================================================================


@pytest.mark.asyncio
async def test_update_detail_description(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.patch(
        f"/items/{item_id}/details/{detail_id}",
        json={"description": "Updated description"},
    )
    assert r.status_code == 200
    assert r.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_detail_notes(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.patch(
        f"/items/{item_id}/details/{detail_id}",
        json={"notes": "Updated notes"},
    )
    assert r.status_code == 200
    assert r.json()["notes"] == "Updated notes"


@pytest.mark.asyncio
async def test_update_detail_clear_notes(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.patch(
        f"/items/{item_id}/details/{detail_id}",
        json={"notes": None},
    )
    assert r.status_code == 200
    assert r.json()["notes"] is None


@pytest.mark.asyncio
async def test_update_detail_group(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.patch(
        f"/items/{item_id}/details/{detail_id}",
        json={"group_id": "operations"},
    )
    assert r.status_code == 200
    assert r.json()["group_id"] == "operations"


@pytest.mark.asyncio
async def test_update_detail_invalid_group_422(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.patch(
        f"/items/{item_id}/details/{detail_id}",
        json={"group_id": "nonexistent"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_detail_not_found(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.patch(
        f"/items/{item_id}/details/99999",
        json={"description": "X"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_detail_wrong_item_404(client: AsyncClient, seed_groups):
    """Detail exists but belongs to a different item."""
    r1 = await client.post(
        "/items/",
        json={
            "name": "ItemA",
            "details": [{"description": "A", "group_id": "engineering"}],
        },
    )
    r2 = await client.post(
        "/items/",
        json={
            "name": "ItemB",
            "details": [{"description": "B", "group_id": "engineering"}],
        },
    )
    detail_id_a = r1.json()["details"][0]["id"]
    item_b_id = r2.json()["id"]

    # Try to patch detail from ItemA using ItemB's path
    r = await client.patch(
        f"/items/{item_b_id}/details/{detail_id_a}",
        json={"description": "Hijack attempt"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_detail_noop(client: AsyncClient, seed_item):
    """PATCH with empty body should succeed and return unchanged data."""
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    original_desc = seed_item["details"][0]["description"]
    r = await client.patch(f"/items/{item_id}/details/{detail_id}", json={})
    assert r.status_code == 200
    assert r.json()["description"] == original_desc


# =========================================================================
# DELETE DETAIL
# =========================================================================


@pytest.mark.asyncio
async def test_delete_detail(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    detail_id = seed_item["details"][0]["id"]
    r = await client.delete(f"/items/{item_id}/details/{detail_id}")
    assert r.status_code == 204

    # Verify the item still exists but has one fewer detail
    r = await client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert len(r.json()["details"]) == 1


@pytest.mark.asyncio
async def test_delete_detail_not_found(client: AsyncClient, seed_item):
    item_id = seed_item["id"]
    r = await client.delete(f"/items/{item_id}/details/99999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_detail_wrong_item_404(client: AsyncClient, seed_groups):
    """Detail exists but belongs to a different item."""
    r1 = await client.post(
        "/items/",
        json={
            "name": "ItemX",
            "details": [{"description": "X", "group_id": "engineering"}],
        },
    )
    r2 = await client.post(
        "/items/",
        json={
            "name": "ItemY",
            "details": [{"description": "Y", "group_id": "engineering"}],
        },
    )
    detail_id_x = r1.json()["details"][0]["id"]
    item_y_id = r2.json()["id"]

    r = await client.delete(f"/items/{item_y_id}/details/{detail_id_x}")
    assert r.status_code == 404
