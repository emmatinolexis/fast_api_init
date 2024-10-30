from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import Date, cast
from sqlalchemy.orm import Session, joinedload

from app.model.inventory import Inventory
from app.model.order import Order, OrderDeviceAssignment
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload
from app.util.enums import OrderStatus


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
                    order_status=OrderStatus.PROCESSING,
                    installation_request=order_payload.installation_request,
                )
                session.add(order_data)
                session.commit()
                session.refresh(order_data)
                return order_data
            except Exception as e:
                session.rollback()
                raise e

    def get_all_orders(
        self, page=1, page_size=10, search_query=None, start_date=None, end_date=None
    ):
        with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                base_query = session.query(Order).options(
                    joinedload(Order.order_inventories)
                    .joinedload(OrderDeviceAssignment.inventory)
                    .joinedload(Inventory.images),
                    joinedload(Order.order_shipping_address),
                )

                if search_query:
                    base_query = (
                        base_query.join(OrderDeviceAssignment)
                        .join(Inventory)
                        .filter(Inventory.device_name.ilike(f"%{search_query}%"))
                    )

                if start_date:
                    base_query = base_query.filter(
                        cast(Order.created_at, Date) >= start_date
                    )

                if end_date:
                    base_query = base_query.filter(
                        cast(Order.created_at, Date) <= end_date
                    )

                # Sort by 'created_at' in descending order
                base_query = base_query.order_by(Order.created_at.desc())

                total_orders = base_query.count()
                fulfilled_orders = base_query.filter(
                    Order.order_status == OrderStatus.DELIVERED
                ).count()
                paginated_orders = base_query.offset(offset).limit(page_size).all()

                return {
                    "orders": paginated_orders,
                    "total_orders": total_orders,
                    "total_pages": (total_orders + page_size - 1) // page_size,
                    "current_page": page,
                    "page_size": page_size,
                    "fulfilled_orders": fulfilled_orders,
                }
            except Exception as e:
                session.rollback()
                raise e

    def update_order_status(self, order_uuid: str, status: str):
        with self.session_factory() as session:
            try:
                order_to_update = (
                    session.query(Order).filter_by(uuid=order_uuid).first()
                )

                if not order_to_update:
                    raise Exception("Order not found")

                order_to_update.order_status = status
                session.commit()
                session.refresh(order_to_update)

                order = (
                    session.query(Order)
                    .filter_by(uuid=order_uuid)
                    .options(
                        joinedload(Order.order_inventories)
                        .joinedload(OrderDeviceAssignment.inventory)
                        .joinedload(Inventory.images),
                        joinedload(Order.order_shipping_address),
                    )
                    .first()
                )

                return order
            except Exception as e:
                session.rollback()
                raise e
