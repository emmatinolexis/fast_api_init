from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.default_device_gateway_configuration import (
    DefaultDeviceGateWayConfiguration,
)
from app.repository.base_repository import BaseRepository


class DefaultDeviceGatewayConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DefaultDeviceGateWayConfiguration)

    def create_gateway_configuration(self, data):
        with self.session_factory() as session:
            gateway_config = self.model(**data)
            session.add(gateway_config)
            session.commit()
            session.refresh(gateway_config)
            return gateway_config
