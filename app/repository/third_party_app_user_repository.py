from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.third_party_app import ThirdPartyAppUser
from app.repository.base_repository import BaseRepository


class ThirdPartAppUserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ThirdPartyAppUser)

    def get_app_users(self):
        with self.session_factory() as session:
            app_users = (
                session.query(self.model)
                .options(joinedload(self.model.third_party_app))
                .all()
            )
            return app_users
