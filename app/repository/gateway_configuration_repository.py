from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.model.gateway_configuration import GatewayConfiguration
from app.repository.base_repository import BaseRepository


class GatewayConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, GatewayConfiguration)
        self.session_factory = session_factory

    def get_gateway_configuration_by_uuid(self, uuid: str):
        with self.session_factory() as session:
            config = session.query(self.model).filter_by(uuid=uuid).first()
            if not config:
                raise NotFoundError("Gateway configuration not found")
            return config

    def create_gateway_configuration(self, data):
        with self.session_factory() as session:
            gateway_config = self.model(**data)
            session.add(gateway_config)
            session.commit()
            session.refresh(gateway_config)
            return gateway_config

    def update_gateway_configuration_by_uuid(self, uuid: str, data):
        with self.session_factory() as session:
            gateway_config = session.query(self.model).filter_by(uuid=uuid).first()
            if not gateway_config:
                raise NotFoundError("Gateway configuration not found")
            for key, value in data.items():
                setattr(gateway_config, key, value)
            session.commit()
            session.refresh(gateway_config)
            return gateway_config
