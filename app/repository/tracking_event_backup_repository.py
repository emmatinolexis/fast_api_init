import datetime
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tracking_event_backup import TrackingEventBackup
from app.repository.base_repository import BaseRepository
from sqlalchemy import select, or_


class TrackingEventBackupRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, TrackingEventBackup)

    async def get_backup_by_date_range(self, start_date: str, end_date: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(
                    or_(
                        self.model.start_date == start_date,
                        self.model.end_date == end_date,
                    )
                )
            )
            return result.unique().scalar_one_or_none()
