from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.immobilize_report import ImmobilizerReport
from app.repository.base_repository import BaseRepository


class ImmobilizerReportRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, ImmobilizerReport)

    async def get_all_immobilizer_report(self):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model)
                    .options(joinedload(self.model.user))
                    .options(joinedload(self.model.asset))
                )
                reports = result.scalars().all()
                return reports
            except SQLAlchemyError as e:
                raise e

    async def get_last_immobilizer_action(self, asset_uuid: str):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model)
                    .filter_by(asset_uuid=asset_uuid)
                    .options(joinedload(self.model.asset))
                    .order_by(desc(self.model.created_at))
                    .limit(1)
                )
                action = result.scalars().first()
                return action
            except SQLAlchemyError as e:
                raise e
