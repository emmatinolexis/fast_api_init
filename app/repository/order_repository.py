from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.inventory import Inventory
from app.model.order import Order, OrderDeviceAssignment
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload


class OrderRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderRepository)

    def create_order(self, order_payload: OrderPayload):
        with self.session_factory() as session:
            try:
                order_data = Order(
                    payment_reference_id=order_payload.payment_reference,
                    total_amount=order_payload.total_amount,
                )
                session.add(order_data)
                session.commit()
                session.refresh(order_data)
                return order_data
            except Exception as e:
                session.rollback()
                raise e

    def get_all_orders(self):
        with self.session_factory() as session:
            try:
                orders = (
                    session.query(Order)
                    .options(
                        joinedload(Order.order_inventories)
                        .joinedload(OrderDeviceAssignment.inventory)
                        .joinedload(Inventory.images),
                        joinedload(Order.order_shipping_address),
                    )
                    .all()
                )
                return orders
            except Exception as e:
                session.rollback()
                raise e
