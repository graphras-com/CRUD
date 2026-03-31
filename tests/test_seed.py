import json

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DetailModel, GroupModel, ItemModel
from app.seed import SEED_FILE, seed


def _load_seed():
    return json.loads(SEED_FILE.read_text())


@pytest.mark.asyncio
async def test_seed_loads_all_groups(db_session: AsyncSession):
    await seed(db_session)

    payload = _load_seed()
    result = await db_session.execute(select(func.count(GroupModel.id)))
    assert result.scalar() == len(payload["groups"])


@pytest.mark.asyncio
async def test_seed_loads_all_items(db_session: AsyncSession):
    await seed(db_session)

    payload = _load_seed()
    result = await db_session.execute(select(func.count(ItemModel.id)))
    assert result.scalar() == len(payload["items"])


@pytest.mark.asyncio
async def test_seed_loads_all_details(db_session: AsyncSession):
    await seed(db_session)

    payload = _load_seed()
    total_details = sum(len(i["details"]) for i in payload["items"])

    result = await db_session.execute(select(func.count(DetailModel.id)))
    assert result.scalar() == total_details


@pytest.mark.asyncio
async def test_seed_is_idempotent(db_session: AsyncSession):
    """Calling seed twice should not insert duplicate data."""
    await seed(db_session)

    result1 = await db_session.execute(select(func.count(GroupModel.id)))
    group_count = result1.scalar()
    result2 = await db_session.execute(select(func.count(ItemModel.id)))
    item_count = result2.scalar()

    # Seed again
    await seed(db_session)

    result3 = await db_session.execute(select(func.count(GroupModel.id)))
    assert result3.scalar() == group_count
    result4 = await db_session.execute(select(func.count(ItemModel.id)))
    assert result4.scalar() == item_count


@pytest.mark.asyncio
async def test_seed_group_parent_references_valid(db_session: AsyncSession):
    """Every group with a parent_id should reference an existing group."""
    await seed(db_session)

    result = await db_session.execute(
        select(GroupModel).where(GroupModel.parent_id.isnot(None))
    )
    children = result.scalars().all()
    assert len(children) > 0

    for child in children:
        parent = await db_session.get(GroupModel, child.parent_id)
        assert parent is not None, (
            f"Group '{child.id}' references missing parent '{child.parent_id}'"
        )


@pytest.mark.asyncio
async def test_seed_detail_group_references_valid(db_session: AsyncSession):
    """Every detail's group_id should reference an existing group."""
    await seed(db_session)

    result = await db_session.execute(select(DetailModel))
    details = result.scalars().all()
    assert len(details) > 0

    group_ids_result = await db_session.execute(select(GroupModel.id))
    valid_ids = {row[0] for row in group_ids_result.all()}

    for detail in details:
        assert detail.group_id in valid_ids, (
            f"Detail {detail.id} references unknown group '{detail.group_id}'"
        )


@pytest.mark.asyncio
async def test_seed_file_matches_backup_schema(db_session: AsyncSession):
    """The seed file should have the expected backup payload structure."""
    payload = _load_seed()

    assert "version" in payload
    assert "groups" in payload
    assert "items" in payload
    assert payload["version"] == 1

    for grp in payload["groups"]:
        assert "id" in grp
        assert "label" in grp
        assert "parent_id" in grp

    for item in payload["items"]:
        assert "name" in item
        assert "details" in item
        for d in item["details"]:
            assert "description" in d
            assert "group_id" in d
