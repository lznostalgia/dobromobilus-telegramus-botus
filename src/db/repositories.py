from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Application, Shelter, Pet


async def get_animal_types(session: AsyncSession) -> list[str]:
    result = await session.scalars(
        select(Pet.animal_type)
        .where(Pet.is_available.is_(True))
        .distinct()
        .order_by(Pet.animal_type)
    )
    return list(result)


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


async def get_pets(
    session: AsyncSession,
    shelter_id: int,
    animal_type: str,
) -> list[Pet]:
    result = await session.scalars(
        select(Pet)
        .where(
            Pet.shelter_id == shelter_id,
            Pet.animal_type == animal_type,
            Pet.is_available.is_(True),
        )
        .order_by(Pet.id)
    )
    return list(result)


async def get_pet(
    session: AsyncSession,
    pet_id: int,
) -> Pet | None:
    return await session.scalar(
        select(Pet)
        .options(selectinload(Pet.shelter))
        .where(Pet.id == pet_id)
    )


async def get_applications(
    session: AsyncSession,
    limit: int = 20,
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