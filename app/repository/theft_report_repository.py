from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.theft_reports import TheftReport
from app.repository.base_repository import BaseRepository


class TheftReportRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, TheftReport)

    async def get_incident_reports(self, incident_uuid: str):
        async with self.session_factory() as session:
            reports = await session.execute(
                select(self.model).filter_by(theft_incident_uuid=incident_uuid)
            )
            return reports.scalars().all()
