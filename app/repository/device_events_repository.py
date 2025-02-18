from datetime import datetime
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.device_event import DeviceEvent
from app.model.gas_cylinders import GasCylinder
from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository


class DeviceEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceEvent)

    async def get_device_latest_reading(self, node_id: str):
        async with self.session_factory() as session:
            stmt = (
                select(self.model)
                .filter(self.model.node_id == str(node_id))
                .order_by(self.model.created_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_device_events_between_dates(
        self, node_id: str, start_date: datetime, end_date: datetime
    ):
        async with self.session_factory() as session:
            stmt = (
                select(self.model)
                .filter(
                    self.model.node_id == node_id,
                    self.model.created_at >= start_date,
                    self.model.created_at <= end_date,
                )
                .order_by(self.model.created_at.asc())
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def read_gas_cylinder_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            stmt = select(GasCylinder).filter(GasCylinder.uuid == uuid)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_peripheral_device_by_serial_number(self, serial_number: str):
        async with self.session_factory() as session:
            stmt = select(PeripheralDevice).filter(
                PeripheralDevice.serial_number == serial_number
            )
            result = await session.execute(stmt)
            return result.scalars().first()
