from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.default_device_gateway_configuration import (
    DefaultDeviceGateWayConfiguration,
)
from app.repository.base_repository import BaseRepository


class DefaultDeviceGatewayConfigurationRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, DefaultDeviceGateWayConfiguration)

    async def create_gateway_configuration(self, data):
        async with self.session_factory() as session:
            gateway_config = self.model(**data)
            session.add(gateway_config)
            await session.commit()
            await session.refresh(gateway_config)
            return gateway_config
