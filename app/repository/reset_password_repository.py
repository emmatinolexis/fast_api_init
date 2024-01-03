from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.password_reset_token import PasswordResetToken
from app.repository.base_repository import BaseRepository


class PasswordResetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PasswordResetToken)

    def create_password_reset(self, verification_token: str, user_uuid: str):
        with self.session_factory() as session:
            password_data = self.model(
                user_uuid=user_uuid, verification_token=verification_token
            )
            session.add(password_data)
            session.commit()
            return password_data
