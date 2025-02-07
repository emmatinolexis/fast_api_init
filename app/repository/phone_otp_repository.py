from datetime import datetime, timedelta
from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.phone_otp_token import PhoneOtpToken
from app.repository.base_repository import BaseRepository
from app.util.utils import generate_unique_token


class PhoneOtpTokenRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, PhoneOtpToken)

    async def generate_token(self) -> str:
        async with self.session_factory() as session:
            while True:
                token = generate_unique_token(size=3)
                result = await session.execute(
                    session.query(self.model).filter(self.model.token == token)
                )
                if not result.scalars().first():
                    return token

    async def create_token(self, user_uuid: str) -> PhoneOtpToken:
        async with self.session_factory() as session:
            token = await self.generate_token()
            query = self.model(
                token=token,
                user_uuid=user_uuid,
                expires_at=datetime.now() + timedelta(hours=2),
            )
            try:
                session.add(query)
                await session.commit()
                await session.refresh(query)
            except IntegrityError as e:
                await session.rollback()
                raise e
            except Exception as e:
                await session.rollback()
                raise e
            return query

    async def get_token(self, token: str) -> PhoneOtpToken:
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model).filter(self.model.token == token)
            )
            return result.scalars().first()

    async def delete_by_user_uuid(self, user_id: str):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model).filter(self.model.user_uuid == user_id)
            )
            tokens = result.scalars().all()

            if not tokens:
                return None
            try:
                for token in tokens:
                    await session.delete(token)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise e
            except Exception as e:
                await session.rollback()
                raise e
