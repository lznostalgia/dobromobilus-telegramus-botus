from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Admin

async def is_extra_admin(
    session: AsyncSession,
    telegram_id: int,
) -> bool:
    result = await session.scalar(
        select(Admin.id).where(
            Admin.telegram_id == telegram_id
        )
    )
    return result is not None


async def get_extra_admins(
    session: AsyncSession,
) -> list[Admin]:
    result = await session.scalars(
        select(Admin).order_by(Admin.telegram_id)
    )
    return list(result)


async def add_extra_admin(
    session: AsyncSession,
    telegram_id: int,
) -> bool:
    existing = await session.scalar(
        select(Admin.id).where(
            Admin.telegram_id == telegram_id
        )
    )

    if existing is not None:
        return False

    session.add(Admin(telegram_id=telegram_id))
    await session.flush()
    return True


async def remove_extra_admin(
    session: AsyncSession,
    telegram_id: int,
) -> bool:
    admin = await session.scalar(
        select(Admin).where(
            Admin.telegram_id == telegram_id
        )
    )

    if admin is None:
        return False

    await session.delete(admin)
    await session.flush()
    return True