import pytest

from db.repositories.admin import (
    add_extra_admin,
    remove_extra_admin,
    is_extra_admin,
    get_extra_admins,
)


@pytest.mark.asyncio
async def test_add_admin(session):
    telegram_id = 123456789

    result = await add_extra_admin(session, telegram_id)

    await session.commit()

    assert result is True
    assert await is_extra_admin(session, telegram_id) is True


@pytest.mark.asyncio
async def test_add_duplicate_admin(session):
    telegram_id = 123456789

    first_result = await add_extra_admin(session, telegram_id)
    second_result = await add_extra_admin(session, telegram_id)

    await session.commit()

    assert first_result is True
    assert second_result is False


@pytest.mark.asyncio
async def test_get_admins(session):
    await add_extra_admin(session, 111111111)
    await add_extra_admin(session, 222222222)

    await session.commit()

    admins = await get_extra_admins(session)
    ids = [admin.telegram_id for admin in admins]

    assert ids == [111111111, 222222222]


@pytest.mark.asyncio
async def test_remove_admin(session):
    telegram_id = 123456789

    await add_extra_admin(session, telegram_id)
    await session.commit()

    result = await remove_extra_admin(session, telegram_id)
    await session.commit()

    assert result is True
    assert await is_extra_admin(session, telegram_id) is False


@pytest.mark.asyncio
async def test_remove_nonexistent_admin(session):
    result = await remove_extra_admin(session, 999999999)

    assert result is False