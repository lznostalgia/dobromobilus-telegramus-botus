from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Shelter, Pet


async def get_cities(
    session: AsyncSession,
    animal_type: str,
) -> list[str]:
    result = await session.scalars(
        select(Shelter.city)
        .join(Shelter.pets)
        .where(
            Pet.animal_type == animal_type,
            Pet.is_available.is_(True),
        )
        .distinct()
        .order_by(Shelter.city)
    )
    return list(result)


async def get_shelters(
    session: AsyncSession,
    city: str,
    animal_type: str,
) -> list[Shelter]:
    result = await session.scalars(
        select(Shelter)
        .join(Shelter.pets)
        .where(
            Shelter.city == city,
            Pet.animal_type == animal_type,
            Pet.is_available.is_(True),
        )
        .distinct()
        .order_by(Shelter.id)
    )
    return list(result)