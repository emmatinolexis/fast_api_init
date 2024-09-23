from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.device_confriguration import DeviceConfiguration
from app.repository.base_repository import BaseRepository
from app.util.enums import DeviceConfigurationVersion


class DeviceConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceConfiguration)

    def get_configuration_by_type(
        self, configuration_version: DeviceConfigurationVersion
    ):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.configuration_version == configuration_version)
                .first()
            )
