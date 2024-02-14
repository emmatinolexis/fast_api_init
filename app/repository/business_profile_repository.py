from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.business_profile import BusinessProfile
from app.repository.base_repository import BaseRepository


class BusinessProfileRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, BusinessProfile)

    def get_by_uuid(self, uuid: str) -> BusinessProfile:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.uuid == uuid)
                .first()
            )
