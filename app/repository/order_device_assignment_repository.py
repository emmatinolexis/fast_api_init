from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.order import OrderDeviceAssignment
from app.repository.base_repository import BaseRepository


class OrderDeviceAssignmentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderDeviceAssignment)

    async def create_order_device(self, device, order_uuid: str):
        async with self.session_factory() as session:  # Async session
            try:
                device_data = OrderDeviceAssignment(
                    inventory_uuid=device.inventory_uuid,
                    quantity=device.quantity,
                    order_uuid=order_uuid,
                )
                session.add(device_data)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
