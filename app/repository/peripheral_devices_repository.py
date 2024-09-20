from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType
from sqlalchemy import asc


class PeripheralDeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PeripheralDevice)

    def read_all(self, page=1, page_size=10, device_type=None):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            base_query = session.query(self.model)

            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type.value)

            total_devices = base_query.count()
            total_pages = (total_devices + page_size - 1) // page_size

            paginated_query = (
                base_query.order_by(asc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )
            devices = paginated_query.all()

        return {
            "devices": devices,
            "total_devices": total_devices,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
        }
    
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
        

    def get_user_devices(self,user_uuid,device_type:str=None):
        with self.session_factory() as session:
            base_query = session.query(self.model).filter(self.model.user_uuid == user_uuid)
            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type)
            return base_query.all()
        
        
    def get_business_devices(self,business_uuid,device_type:str=None):
        with self.session_factory() as session:
            base_query = session.query(self.model).filter(self.model.business_profile_uuid == business_uuid)
            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type)
            return base_query.all()