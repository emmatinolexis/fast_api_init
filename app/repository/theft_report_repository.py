from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.theft_reports import TheftReport
from app.repository.base_repository import BaseRepository


class TheftReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, TheftReport)

    def get_incident_reports(self, incident_uuid: str):
        with self.session_factory() as session:
            reports = (
                session.query(self.model)
                .filter_by(theft_incident_uuid=incident_uuid)
                .all()
            )
            return reports
