from contextlib import AbstractAsyncContextManager
from typing import Callable, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.driver_license import DriverLicense
from app.repository.base_repository import BaseRepository


class DriverLicenseRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, DriverLicense)

    async def get_license_by_license_number(self, license_number: str) -> DriverLicense:
        async with self.session_factory() as session:
            query = select(DriverLicense).filter(
                DriverLicense.license_number == license_number
            )
            result = await session.execute(query)
            return result.scalar_.one_or_none()

    async def get_license_by_user_id(self, user_uuid: str) -> DriverLicense:
        async with self.session_factory() as session:
            query = select(DriverLicense).filter(DriverLicense.user_id == user_uuid)
            result = await session.execute(query)
            return result.scalar_.one_or_none()

    async def get_all_licenses(self) -> List[DriverLicense]:
        async with self.session_factory() as session:
            query = select(DriverLicense)
            result = await session.execute(query)
            return list(result.scalars().all())
