from contextlib import AbstractContextManager
from app.repository.base_repository import BaseRepository
from typing import Callable
from app.model.incident import Incident


class IncidentRepository(BaseRepository):
    def __init__(self, session_factory:Callable[..., AbstractContextManager]):
        self.session_factory = session_factory
        super().__init__(session_factory,Incident)

    