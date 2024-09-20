from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType


class PeripheralDeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PeripheralDevice)

    def get_last_device(self, device_type: PeripheralDeviceType):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.device_type == device_type)
                .order_by(self.model.id.desc())
                .first()
            )

    def get_by_serial_number(self, serial_number: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.serial_number == serial_number)
                .first()
            )
