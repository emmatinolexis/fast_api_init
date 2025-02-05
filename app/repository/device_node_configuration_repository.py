from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.constants import (
    GAS_DEVICE_MINIMUM_THRESHOLD,
    PYRO_AMBIENT_TEMPERATURE_THRESHOLD,
    PYRO_FLAMMABLE_SMOKE_THRESHOLD,
    PYRO_HUMIDITY_THRESHOLD,
    PYRO_TARGET_TEMPERATURE_THRESHOLD,
)
from app.model.peripheral_devices import DeviceNodeConfig
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType


class DeviceNodeConfigRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceNodeConfig)

    async def get_device_node_config_by_device_uuid(self, uuid: str) -> DeviceNodeConfig:
        async with self.session_factory() as session:
            stmt = select(self.model).filter(self.model.peripheral_device_uuid == uuid)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def set_peripheral_device_to_default(self, peripheral_device_uuid: str):
        async with self.session_factory() as session:
            stmt = (
                select(self.model)
                .filter(self.model.peripheral_device_uuid == peripheral_device_uuid)
                .options(joinedload(self.model.peripheral_device))
            )
            result = await session.execute(stmt)
            device = result.scalars().first()

            if not device:
                return None 

            if device.peripheral_device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
                device.minimum_threshold = GAS_DEVICE_MINIMUM_THRESHOLD

            if device.peripheral_device.device_type == PeripheralDeviceType.PYROGUARD_NODE_DEVICE:
                device.ambient_temperature_threshold = PYRO_AMBIENT_TEMPERATURE_THRESHOLD
                device.humidity_threshold = PYRO_HUMIDITY_THRESHOLD
                device.target_temperature_threshold = PYRO_TARGET_TEMPERATURE_THRESHOLD
                device.flammable_smoke_threshold = PYRO_FLAMMABLE_SMOKE_THRESHOLD

            await session.commit()
            await session.refresh(device)
            return device

    async def toggle_send_alert_status(self, peripheral_device_uuid: str):
        async with self.session_factory() as session:
            stmt = select(self.model).filter_by(peripheral_device_uuid=peripheral_device_uuid)
            result = await session.execute(stmt)
            device = result.scalars().first()

            if device:
                device.send_alert_status = not device.send_alert_status
                await session.commit()
                await session.refresh(device)

            return device
