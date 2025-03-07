from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.model.base_model import Base


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url,
            pool_size=20,  # Increase pool size
            max_overflow=-1,  # Allow more temporary connections
            pool_timeout=120,  # Increase timeout before error
            echo=False,
        )

        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def connected(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                # await conn.run_sync(User.__table__.select)
                return True
        except Exception as e:
            raise e

    async def close(self) -> None:
        await self._engine.dispose()

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
