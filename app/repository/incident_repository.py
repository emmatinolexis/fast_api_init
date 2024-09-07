from contextlib import AbstractContextManager
from typing import Callable

from app.model.incident import Incident
from app.repository.base_repository import BaseRepository


class IncidentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager]):
        self.session_factory = session_factory
        super().__init__(session_factory, Incident)
