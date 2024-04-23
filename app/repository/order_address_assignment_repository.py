from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.order import OrderAddressAssignment
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload


class OrderAddressAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderAddressAssignment)

    def create_order_address(self, order_payload: OrderPayload, order_uuid: str):
        with self.session_factory() as session:
            try:
                address_data = {
                    "country": order_payload.shipping_address.country,
                    "first_name": order_payload.shipping_address.first_name,
                    "last_name": order_payload.shipping_address.last_name,
                    "email": order_payload.shipping_address.email,
                    "phone_number": order_payload.shipping_address.phone_number,
                    "street_name": order_payload.shipping_address.email,
                    "post_code": order_payload.shipping_address.post_code,
                    "order_uuid": order_uuid,
                }
                session.add(address_data)
                session.commit()
                session.refresh(address_data)
                return address_data
            except Exception as e:
                session.rollback()
                raise e
