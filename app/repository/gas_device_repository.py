from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository


class GasDeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PeripheralDevice)

    async def get_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(PeripheralDevice).filter(PeripheralDevice.uuid == uuid)
            )
            return result.scalars().first()

    async def get_device_by_serial_no(self, device_serial_no: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.serial_number == device_serial_no)
            )
            return result.scalars().first()

    async def search(self, serial_number: Optional[str] = None):
        async with self.session_factory() as session:
            stmt = select(self.model)
            
            if serial_number:
                stmt = stmt.filter(self.model.serial_number.ilike(f"%{serial_number}%"))
            
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_user_devices(self, user_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.user_uuid == user_uuid)
            )
            return result.scalars().all()

    async def get_business_devices(self, business_profile_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.business_profile_uuid == business_profile_uuid)
            )
            return result.scalars().all()

    async def get_building_devices(self, building_uuid: str, device_type: Optional[str] = None):
        async with self.session_factory() as session:
            stmt = select(self.model).filter(self.model.building_uuid == building_uuid)

            if device_type:
                stmt = stmt.filter(self.model.device_type == device_type)

            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_all_devices(self, serial_number: Optional[str] = None, device_type: Optional[str] = None):
        async with self.session_factory() as session:
            stmt = select(self.model)

            if serial_number:
                stmt = stmt.filter(self.model.serial_number.ilike(f"%{serial_number}%"))

            if device_type:
                stmt = stmt.filter(self.model.device_type == device_type)

            result = await session.execute(stmt)
            return result.scalars().all()
