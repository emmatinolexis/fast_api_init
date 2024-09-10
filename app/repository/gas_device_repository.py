from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

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

    def search(self, serial_number: str = None):
        with self.session_factory() as session:
            query = session.query(self.model)
            if serial_number:
                query = query.filter(
                    self.model.serial_number.ilike(f"%{serial_number}%")
                )
            return query.all()

    def get_user_devices(self, user_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .all()
            )

    def get_business_devices(self, business_profile_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_profile_uuid)
                .all()
            )

    def get_building_devices(self, building_uuid: str, device_type: str = None):
        with self.session_factory() as session:
            query = session.query(self.model).filter(
                self.model.building_uuid == building_uuid
            )
            if device_type:
                query = query.filter(self.model.device_type == device_type)
            return query.all()

    def get_all_devices(self, serial_number: str = None, device_type: str = None):
        with self.session_factory() as session:
            query = session.query(self.model)

            # Apply filtering based on serial_number if provided
            if serial_number:
                query = query.filter(
                    self.model.serial_number.ilike(f"%{serial_number}%")
                )

            # Apply filtering based on device_type if provided
            if device_type:
                query = query.filter(self.model.device_type == device_type)

            # Pagination

            return query.all()
