from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.device_confriguration import DeviceConfiguration
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType


class DeviceConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceConfiguration)

    def get_configuration_by_type(self, device_type: PeripheralDeviceType):
        with self.session_factory() as session:
            # Assuming 'id' is the auto-incrementing primary key or 'created_at' is a timestamp field
            return (
                session.query(self.model)
                .filter(self.model.device_type == device_type)
                .order_by(
                    self.model.id.desc()
                )  # or .order_by(self.model.created_at.desc())
                .first()
            )
