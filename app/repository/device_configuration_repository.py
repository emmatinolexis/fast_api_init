from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.device_confriguration import DeviceConfiguration
from app.repository.base_repository import BaseRepository
from app.util.enums import DeviceConfigurationVersion


class DeviceConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceConfiguration)

    async def get_configuration_by_type(
        self, configuration_version: DeviceConfigurationVersion
    ):
        async with self.session_factory() as session:
            stmt = select(self.model).filter(self.model.configuration_version == configuration_version)
            result = await session.execute(stmt)
            return result.scalars().first()
