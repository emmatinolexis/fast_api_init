from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.order import OrderShippingAddress
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload


class OrderShippingAddressRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderShippingAddress)

    async def create_order_address(self, order_payload: OrderPayload, order_uuid: str):
        async with self.session_factory() as session:
            try:
                address = OrderShippingAddress(
                    country=order_payload.shipping_address.country,
                    first_name=order_payload.shipping_address.first_name,
                    last_name=order_payload.shipping_address.last_name,
                    email=order_payload.shipping_address.email,
                    phone=order_payload.shipping_address.phone,
                    address={
                        "address_name": order_payload.shipping_address.address.address_name,
                        "lat": order_payload.shipping_address.address.lat,
                        "lng": order_payload.shipping_address.address.lng,
                    },
                    post_code=order_payload.shipping_address.post_code,
                    order_uuid=order_uuid,
                    city=order_payload.shipping_address.city,
                )
                session.add(address)
                await session.commit()
                await session.refresh(address)
                return address
            except Exception as e:
                await session.rollback()
                raise e
