from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.asset import Asset
from app.model.fine_report import FineReport
from app.repository.base_repository import BaseRepository


class FineReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, FineReport)

    def get_fine_reports(self):
        with self.session_factory() as session:
            make = (
                session.query(self.model)
                .options(joinedload(self.model.asset).joinedload(Asset.vehicle_owner))
                .all()
            )
            return make

    def get_fine_report(self, uuid: str):
        with self.session_factory() as session:
            fine = (
                session.query(self.model)
                .filter(self.model.uuid == uuid)
                .options(joinedload(self.model.asset))
                .first()
            )
            return fine
