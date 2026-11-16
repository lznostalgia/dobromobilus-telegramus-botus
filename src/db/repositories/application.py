from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Application, Pet

async def get_applications(
    session: AsyncSession,
    limit: int = 10,
) -> list[Application]:
    result = await session.scalars(
        select(Application)
        .options(
            selectinload(Application.pet)
            .selectinload(Pet.shelter)
        )
        .order_by(Application.created_at.desc())
        .limit(limit)
    )
    return list(result)


async def create_application(
    session: AsyncSession,
    telegram_user_id: int,
    telegram_username: str | None,
    pet_id: int,
) -> str:
    pet = await session.scalar(
        select(Pet).where(
            Pet.id == pet_id,
            Pet.is_available.is_(True),
        )
    )

    if pet is None:
        return "unavailable"

    existing = await session.scalar(
        select(Application.id).where(
            Application.telegram_user_id == telegram_user_id,
            Application.pet_id == pet_id,
        )
    )

    if existing is not None:
        return "duplicate"

    session.add(
        Application(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            pet_id=pet_id,
        )
    )

    await session.flush()
    return "created"