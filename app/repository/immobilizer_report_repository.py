from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.model.immobilize_report import ImmobilizerReport
from app.repository.base_repository import BaseRepository


class ImmobilizerReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ImmobilizerReport)

    def get_all_immobilizer_report(self):
        with self.session_factory() as session:
            try:
                reports = (
                    session.query(self.model)
                    .options(joinedload(self.model.user))
                    .options(joinedload(self.model.asset))
                    .all()
                )
                return reports
            except Exception as e:
                raise e

    def get_last_immobilizer_action(self, asset_uuid: str):
        with self.session_factory() as session:
            try:
                action = (
                    session.query(self.model)
                    .filter_by(asset_uuid=asset_uuid)
                    .options(joinedload(self.model.asset))
                    .order_by(desc(self.model.created_at))
                    .first()
                )
                return action
            except Exception as e:
                raise e
