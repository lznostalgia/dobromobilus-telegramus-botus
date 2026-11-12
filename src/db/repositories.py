from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Applications, Fosters, Pets



async def get_animal_types(session: AsyncSession) -> list[str]:
    result = await session.scalars(
        select(Pets.animal_type)
        .distinct()
        .order_by(Pets.animal_type)
    )
    return list(result)


async def get_cities(session: AsyncSession) -> list[str]:
    result = await session.scalars(
        select(Fosters.city)
        .distinct()
        .order_by(Fosters.city)
    )
    return list(result)


async def get_fosters(
    session: AsyncSession,
    city: str,
) -> list[Fosters]:
    result = await session.scalars(
        select(Fosters)
        .where(Fosters.city == city)
        .order_by(Fosters.id)
    )
    return list(result)


async def get_pets(
    session: AsyncSession,
    shelter_id: int,
    animal_type: str,
) -> list[Pets]:
    result = await session.scalars(
        select(Pets)
        .where(
            Pets.shelter_id == shelter_id,
            Pets.animal_type == animal_type,
            Pets.is_available.is_(True),
        )
        .order_by(Pets.id)
    )
    return list(result)


async def get_applications(session: AsyncSession) -> list[Applications]:
    result = await session.scalars(
        select(Applications).order_by(Applications.created_at.desc())
    )
    return list(result)
