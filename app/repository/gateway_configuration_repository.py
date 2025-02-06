from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext import AsynSession

from app.core.exceptions import NotFoundError
from app.model.gateway_configuration import GatewayConfiguration
from app.repository.base_repository import BaseRepository


class GatewayConfigurationRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        super().__init__(session_factory, GatewayConfiguration)
        self.session_factory = session_factory

    async def get_gateway_configuration_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(uuid=uuid))
            config = result.scalars().first()

            if not config:
                raise NotFoundError("Gateway configuration not found")

            return config

    async def create_gateway_configuration(self, data):
        async with self.session_factory() as session:
            gateway_config = self.model(**data)
            session.add(gateway_config)
            await session.commit()
            await session.refresh(gateway_config)
            return gateway_config

    async def update_gateway_configuration_by_uuid(self, uuid: str, data):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(uuid=uuid))
            gateway_config = result.scalars().first()

            if not gateway_config:
                raise NotFoundError("Gateway configuration not found")

            for key, value in data.items():
                setattr(gateway_config, key, value)

            await session.commit()
            await session.refresh(gateway_config)
            return gateway_config
