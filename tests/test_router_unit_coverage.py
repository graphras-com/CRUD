"""Unit-level tests that exercise router and utility branches directly.

These tests call the HTTP endpoints via the test client rather than
importing internal router functions, making them compatible with the
generic CRUD framework.
"""

import pytest
from httpx import AsyncClient

from app.database import get_db
from app.main import app, lifespan


@pytest.mark.asyncio
async def test_groups_router_branches(client: AsyncClient):
    """Exercise all group CRUD branches through HTTP."""
    # Create root and child
    r = await client.post(
        "/groups/",
        json={"id": "engineering", "parent_id": None, "label": "Engineering"},
    )
    assert r.status_code == 201

    r = await client.post(
        "/groups/",
        json={
            "id": "engineering.backend",
            "parent_id": "engineering",
            "label": "Backend",
        },
    )
    assert r.status_code == 201

    # List
    r = await client.get("/groups/")
    assert r.status_code == 200
    ids = [g["id"] for g in r.json()]
    assert "engineering" in ids
    assert "engineering.backend" in ids

    # Get by ID
    r = await client.get("/groups/engineering.backend")
    assert r.status_code == 200
    assert r.json()["id"] == "engineering.backend"

    # Duplicate 409
    r = await client.post(
        "/groups/",
        json={"id": "engineering", "parent_id": None, "label": "Duplicate"},
    )
    assert r.status_code == 409

    # Bad parent 422
    r = await client.post(
        "/groups/",
        json={"id": "orphan", "parent_id": "missing", "label": "Orphan"},
    )
    assert r.status_code == 422

    # Update label
    r = await client.patch(
        "/groups/engineering",
        json={"label": "Eng Team", "parent_id": None},
    )
    assert r.status_code == 200
    assert r.json()["label"] == "Eng Team"

    # Update missing 404
    r = await client.patch("/groups/missing", json={"label": "x"})
    assert r.status_code == 404

    # Update with invalid parent 422
    r = await client.patch(
        "/groups/engineering.backend",
        json={"parent_id": "missing-parent"},
    )
    assert r.status_code == 422

    # Delete missing 404
    r = await client.delete("/groups/missing")
    assert r.status_code == 404

    # Create an item referencing the group to test protected delete
    r = await client.post(
        "/items/",
        json={
            "name": "Widget",
            "details": [
                {
                    "description": "A core widget",
                    "notes": None,
                    "group_id": "engineering",
                }
            ],
        },
    )
    assert r.status_code == 201

    # Delete unreferenced child
    r = await client.delete("/groups/engineering.backend")
    assert r.status_code == 204

    # Delete referenced parent (409)
    r = await client.delete("/groups/engineering")
    assert r.status_code == 409

    # Get deleted group (404)
    r = await client.get("/groups/engineering.backend")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_items_and_details_router_branches(client: AsyncClient):
    """Exercise all item and detail CRUD branches through HTTP."""
    # Setup groups
    await client.post(
        "/groups/",
        json={"id": "engineering", "parent_id": None, "label": "Engineering"},
    )
    await client.post(
        "/groups/",
        json={
            "id": "engineering.backend",
            "parent_id": "engineering",
            "label": "Backend",
        },
    )

    # Create item
    r = await client.post(
        "/items/",
        json={
            "name": "Widget",
            "details": [
                {
                    "description": "A reusable component",
                    "notes": "Used in production",
                    "group_id": "engineering.backend",
                }
            ],
        },
    )
    assert r.status_code == 201
    item = r.json()
    item_id = item["id"]

    # List with search and group filter
    r = await client.get("/items/?q=Widget&group=engineering.backend")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Widget"

    # Get by ID
    r = await client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id

    # Get missing 404
    r = await client.get("/items/99999")
    assert r.status_code == 404

    # Duplicate create 409
    r = await client.post(
        "/items/",
        json={
            "name": "Widget",
            "details": [
                {
                    "description": "dup",
                    "notes": None,
                    "group_id": "engineering",
                }
            ],
        },
    )
    assert r.status_code == 409

    # Create with bad group 422
    r = await client.post(
        "/items/",
        json={
            "name": "Ghost",
            "details": [
                {
                    "description": "Bad ref",
                    "notes": None,
                    "group_id": "missing",
                }
            ],
        },
    )
    assert r.status_code == 422

    # Create second item
    r = await client.post(
        "/items/",
        json={
            "name": "Gadget",
            "details": [
                {
                    "description": "A useful gadget",
                    "notes": None,
                    "group_id": "engineering",
                }
            ],
        },
    )
    assert r.status_code == 201
    second = r.json()

    # Update to duplicate name 409
    r = await client.patch(f"/items/{second['id']}", json={"name": "Widget"})
    assert r.status_code == 409

    # Rename
    r = await client.patch(f"/items/{item_id}", json={"name": "Widget Pro"})
    assert r.status_code == 200
    assert r.json()["name"] == "Widget Pro"

    # Update missing 404
    r = await client.patch("/items/99999", json={"name": "x"})
    assert r.status_code == 404

    # Add detail
    r = await client.post(
        f"/items/{item_id}/details",
        json={
            "description": "Alternative implementation",
            "notes": None,
            "group_id": "engineering",
        },
    )
    assert r.status_code == 201
    detail = r.json()
    assert detail["description"] == "Alternative implementation"

    # Add detail to missing item 404
    r = await client.post(
        "/items/99999/details",
        json={
            "description": "x",
            "notes": None,
            "group_id": "engineering",
        },
    )
    assert r.status_code == 404

    # Add detail with bad group 422
    r = await client.post(
        f"/items/{item_id}/details",
        json={
            "description": "x",
            "notes": None,
            "group_id": "missing",
        },
    )
    assert r.status_code == 422

    # Update detail
    r = await client.patch(
        f"/items/{item_id}/details/{detail['id']}",
        json={"description": "Updated implementation"},
    )
    assert r.status_code == 200
    assert r.json()["description"] == "Updated implementation"

    # Update missing detail 404
    r = await client.patch(
        f"/items/{item_id}/details/99999",
        json={"description": "x"},
    )
    assert r.status_code == 404

    # Update detail with bad group 422
    r = await client.patch(
        f"/items/{item_id}/details/{detail['id']}",
        json={"group_id": "missing"},
    )
    assert r.status_code == 422

    # Delete missing detail 404
    r = await client.delete(f"/items/{item_id}/details/99999")
    assert r.status_code == 404

    # Delete detail
    r = await client.delete(f"/items/{item_id}/details/{detail['id']}")
    assert r.status_code == 204

    # Delete missing item 404
    r = await client.delete("/items/99999")
    assert r.status_code == 404

    # Delete second item
    r = await client.delete(f"/items/{second['id']}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_backup_router_branches(client: AsyncClient):
    """Exercise backup and restore through HTTP."""
    payload = {
        "version": 1,
        "groups": [
            {"id": "dept.team", "parent_id": "dept", "label": "Team"},
            {"id": "dept", "parent_id": None, "label": "Department"},
        ],
        "items": [
            {
                "name": "Report Generator",
                "details": [
                    {
                        "description": "Generates weekly reports",
                        "notes": None,
                        "group_id": "dept.team",
                    }
                ],
            }
        ],
    }

    r = await client.post("/backup/restore", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["groups"] == 2
    assert body["items"] == 1

    r = await client.get("/backup/")
    assert r.status_code == 200
    backup_data = r.json()
    assert backup_data["version"] == 1
    assert len(backup_data["groups"]) == 2
    assert backup_data["items"][0]["name"] == "Report Generator"


@pytest.mark.asyncio
async def test_lifespan_runs_startup_and_shutdown(monkeypatch):
    calls = {"create_all": 0, "seed": 0, "dispose": 0}

    class FakeConn:
        async def run_sync(self, fn):
            calls["create_all"] += 1

    class FakeBegin:
        async def __aenter__(self):
            return FakeConn()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        def begin(self):
            return FakeBegin()

        async def dispose(self):
            calls["dispose"] += 1

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    async def fake_seed(_db, _registry, _seed_file):
        calls["seed"] += 1

    monkeypatch.setattr("app.main.engine", FakeEngine())
    monkeypatch.setattr("app.main.async_session", lambda: FakeSession())
    monkeypatch.setattr("app.main.seed_from_file", fake_seed)

    async with lifespan(app):
        pass

    assert calls == {"create_all": 1, "seed": 1, "dispose": 1}


@pytest.mark.asyncio
async def test_get_db_dependency_yields_session():
    gen = get_db()
    session = await anext(gen)
    assert session is not None
    await gen.aclose()
