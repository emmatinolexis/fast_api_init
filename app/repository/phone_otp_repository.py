import secrets
from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.model.phone_otp_token import PhoneOtpToken
from app.repository.base_repository import BaseRepository


class PhoneOtpTokenRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PhoneOtpToken)

    def generate_token(self) -> str:
        with self.session_factory() as session:
            while True:
                token = secrets.token_hex(3).upper()
                if not session.query(self.model).filter(self.model.token == token).first():
                    return token

    def create_token(self, user_uuid: str) -> PhoneOtpToken:
        with self.session_factory() as session:
            token = self.generate_token()
            query = self.model(
                token=token,
                user_uuid=user_uuid,
                expires_at=datetime.now() + timedelta(hours=2)
            )
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
            except IntegrityError as e:
                raise e
            except Exception as e:
                raise e
            return query
