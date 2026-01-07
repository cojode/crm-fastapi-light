from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class AsyncDatabase:

    def __init__(self, url: str, isolation_level: str | None = None) -> None:
        self._async_engine: AsyncEngine = create_async_engine(
            url=url,
            pool_pre_ping=True,
            isolation_level=isolation_level or "READ COMMITTED",
        )
        self._async_session: async_sessionmaker = async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._async_engine

    @property
    def session_factory(self) -> async_sessionmaker:
        return self._async_session

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        session: AsyncSession = self._async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_tables(
        self, base: DeclarativeBase, with_drop: bool = False
    ) -> None:
        async with self._async_engine.begin() as conn:
            if with_drop:
                await conn.run_sync(base.metadata.drop_all)

            await conn.run_sync(base.metadata.create_all)

    async def close_db(self) -> None:
        await self._async_engine.dispose()
