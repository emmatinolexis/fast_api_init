from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.gas_cylinders import GasDevice
from app.repository.base_repository import BaseRepository


class GasDeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, GasDevice)

    def get_by_uuid(self, uuid: str):
        with self.session_factory() as session:
            return session.query(GasDevice).filter(GasDevice.uuid == uuid).first()

    def get_device_by_serial_no(self, device_serial_no: str):
        with self.session_factory() as session:
            device = (
                session.query(self.model)
                .filter(self.model.serial_number == device_serial_no)
                .first()
            )
            return device
