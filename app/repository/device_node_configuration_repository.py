from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.peripheral_devices import DeviceNodeConfig
from app.repository.base_repository import BaseRepository


class DeviceNodeConfigRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceNodeConfig)

    def get_device_node_config_by_device_uuid(self, uuid: str) -> DeviceNodeConfig:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.peripheral_device_uuid == uuid)
                .first()
            )
