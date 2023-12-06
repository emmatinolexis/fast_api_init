from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.email_verification import EmailVerification
from app.repository.base_repository import BaseRepository


class EmailVerificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, EmailVerification)

    def get_by_token(self, token: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.verification_token == token)
                .first()
            )

    def delete_by_verification_token(self, token: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(self.model.verification_token == token)
                .first()
            )
            session.delete(query)
            session.commit()
