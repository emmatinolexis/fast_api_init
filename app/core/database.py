from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.model.base_model import Base


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=False)
        self._session_factory = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def connected(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute("SELECT 1")
                return True
        except Exception:
            return False

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
