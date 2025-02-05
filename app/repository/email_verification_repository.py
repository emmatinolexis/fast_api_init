from contextlib import AbstractAsyncContextManager
from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.email_verification import EmailVerification
from app.repository.base_repository import BaseRepository


class EmailVerificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        super().__init__(session_factory, EmailVerification)

    async def read_by_user_uuid(self, uuid: str) -> Optional[EmailVerification]:
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.user_uuid == uuid)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[EmailVerification]:
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.verification_token == token)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def delete_by_verification_token(self, token: str) -> None:
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.verification_token == token)
                result = await session.execute(query)
                verification = result.scalar_one_or_none()
                
                if verification:
                    await session.delete(verification)
                    await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def delete_by_user_uuid(self, uuid: str) -> None:
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.user_uuid == uuid)
                result = await session.execute(query)
                verification = result.scalar_one_or_none()
                
                if verification:
                    await session.delete(verification)
                    await session.commit()
            except Exception as e:
                await session.rollback()
                raise e