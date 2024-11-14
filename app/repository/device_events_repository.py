from contextlib import AbstractContextManager
from typing import Callable
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.model.device_event import DeviceEvent
from app.model.gas_cylinders import GasCylinder
from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository


class DeviceEventRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceEvent)

    def get_device_latest_reading(self, node_id: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.node_id == str(node_id))
                .order_by(self.model.created_at.desc())
                .first()
            )

    def get_device_events_between_dates(
        self, node_id: str, start_date: datetime, end_date: datetime
    ):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(
                    self.model.node_id == node_id,
                    self.model.created_at >= start_date,
                    self.model.created_at <= end_date,
                )
                .order_by(self.model.created_at.asc())
                .all()
            )

    def read_gas_cylinder_by_uuid(self, uuid: str):
        with self.session_factory() as session:
            return (
                session.query(GasCylinder)
                .filter(GasCylinder.uuid == uuid)
                .first()
            )

    def get_peripheral_device_by_serial_number(self, serial_number: str):
        with self.session_factory() as session:
            return (
                session.query(PeripheralDevice)
                .filter(PeripheralDevice.serial_number == serial_number)
                .first()
            )
