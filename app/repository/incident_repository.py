from contextlib import AbstractContextManager
from typing import Callable

from app.model.incident import Incident
from app.repository.base_repository import BaseRepository


class IncidentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager]):
        self.session_factory = session_factory
        super().__init__(session_factory, Incident)


    def get_all_incidents(self, incident_type: str = None):
        with self.session_factory() as session:
            if incident_type:
                return (
                    session.query(self.model)
                    .filter_by(incident_type=incident_type)
                    .all()
                )
            return (
                self.read_all()
            )

