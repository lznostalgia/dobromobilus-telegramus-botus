from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from .base import Base
from . import models


class Database:

    def __init__(self, url: str):
        self.engine = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.create_all
            )

    async def close(self) -> None:
        await self.engine.dispose()