from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.order import OrderDeviceAssignment
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload


class OrderDeviceAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderDeviceAssignment)

    def create_order_devices(self, order_payload: OrderPayload, order_uuid: str):
        with self.session_factory() as session:
            try:
                for device in order_payload.devices:
                    device_data = {
                        "device_uuid": device.device_uuid,
                        "quantity": device.quantity,
                        "order_uuid": order_uuid,
                    }
                    session.add(device_data)
                    session.commit()
                    session.refresh(device_data)
                msg = "Order device created successfully"
                return msg
            except Exception as e:
                session.rollback()
                raise e
