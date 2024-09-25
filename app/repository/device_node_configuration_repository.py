from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.peripheral_devices import DeviceNodeConfig
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType
from app.core.constants import (
    GAS_DEVICE_MINIMUM_THRESHOLD,
    PYRO_HUMIDITY_THRESHOLD,
    PYRO_AMBIENT_TEMPERATURE_THRESHOLD,
    PYRO_FLAMMABLE_SMOKE_THRESHOLD,
    PYRO_TARGET_TEMPERATURE_THRESHOLD
)


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

    def set_peripheral_device_to_default(self, peripheral_device_uuid: str):
        with self.session_factory() as session:
            device = (
                session.query(self.model)
                .filter(self.model.peripheral_device_uuid == peripheral_device_uuid)
                .options(joinedload(self.model.peripheral_device))
                .first()
            )
            return
            if device.peripheral_device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
                device.minimum = GAS_DEVICE_MINIMUM_THRESHOLD

            if device.peripheral_device.device_type == PeripheralDeviceType.PYROGUARD_NODE_DEVICE:
                device.ambient_temperature_threshold = PYRO_AMBIENT_TEMPERATURE_THRESHOLD
                device.humidity_threshold = PYRO_HUMIDITY_THRESHOLD
                device.target_temperature_threshold = PYRO_TARGET_TEMPERATURE_THRESHOLD,
                device.flammable_smoke_threshold = PYRO_FLAMMABLE_SMOKE_THRESHOLD

            session.refresh(device)
            session.commit()
            return device
