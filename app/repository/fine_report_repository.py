from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.asset import Asset
from app.model.fine_report import FineReport
from app.repository.base_repository import BaseRepository


class FineReportRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, FineReport)

    async def get_fine_reports(self):
        async with self.session_factory() as session:
            query = await session.execute(
                select(self.model).options(
                    joinedload(self.model.asset).joinedload(Asset.vehicle_owner)
                )
            )
            result = query.scalars().all()
            return result

    async def get_fine_report(self, uuid: str):
        async with self.session_factory() as session:
            query = await session.execute(
                select(self.model)
                .filter(self.model.uuid == uuid)
                .options(joinedload(self.model.asset))
            )
            result = query.scalars().first()
            return result
