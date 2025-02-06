from contextlib import AbstractAsyncContextManager
from datetime import datetime, timedelta
from typing import Callable, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import Date, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.inventory import Inventory
from app.model.order import Order, OrderDeviceAssignment
from app.repository.base_repository import BaseRepository
from app.schema.order_schema import OrderPayload
from app.util.enums import OrderStatus
from app.util.utils import calculate_percentage_change, parse_date


class OrderRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, OrderRepository)

    async def get_order_by_uuid(self, order_uuid: UUID):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(Order)
                    .options(
                        joinedload(Order.order_inventories)
                        .joinedload(OrderDeviceAssignment.inventory)
                        .joinedload(Inventory.images),
                        joinedload(Order.order_shipping_address),
                    )
                    .filter(Order.uuid == order_uuid)
                )
                order = result.scalars().first()
                return order
            except Exception as e:
                await session.rollback()
                raise e

    async def create_order(self, order_payload: OrderPayload):
        async with self.session_factory() as session:
            try:
                order_data = Order(
                    payment_reference_id=order_payload.payment_reference,
                    total_amount=order_payload.total_amount,
                    order_status=OrderStatus.PROCESSING,
                    installation_request=order_payload.installation_request,
                )
                session.add(order_data)
                await session.commit()
                await session.refresh(order_data)
                return order_data
            except Exception as e:
                await session.rollback()
                raise e

    async def _get_base_query(self):
        return (
            select(Order)
            .options(
                joinedload(Order.order_inventories)
                .joinedload(OrderDeviceAssignment.inventory)
                .joinedload(Inventory.images),
                joinedload(Order.order_shipping_address),
            )
            .order_by(Order.created_at.desc())
        )

    async def get_all_orders(
        self,
        page=1,
        page_size=10,
        search_query=None,
        start_date=None,
        end_date=None,
        status=None,
    ):
        async with self.session_factory() as session:
            if start_date and end_date:
                try:
                    parsed_start_str = parse_date(start_date)
                    parsed_end_str = parse_date(end_date)

                    current_start_date = datetime.strptime(parsed_start_str, "%Y-%m-%d")
                    current_end_date = datetime.strptime(parsed_end_str, "%Y-%m-%d")
                except ValueError as ve:
                    raise ValueError(f"Date parsing error: {ve}")
            else:
                if end_date:
                    try:
                        parsed_end_str = parse_date(end_date)
                        current_end_date = datetime.combine(
                            datetime.strptime(parsed_end_str, "%Y-%m-%d"),
                            datetime.max.time(),
                        )
                    except ValueError as ve:
                        raise ValueError(f"Date parsing error: {ve}")
                else:
                    current_end_date = datetime.utcnow()

                if start_date:
                    try:
                        parsed_start_str = parse_date(start_date)
                        current_start_date = datetime.combine(
                            datetime.strptime(parsed_start_str, "%Y-%m-%d"),
                            datetime.min.time(),
                        )
                    except ValueError as ve:
                        raise ValueError(f"Date parsing error: {ve}")
                else:
                    current_start_date = current_end_date - relativedelta(months=12)

            delta = current_end_date - current_start_date
            previous_start_date = current_start_date - delta
            previous_end_date = current_start_date - timedelta(seconds=1)

            base_query = await self._get_base_query(session)

            query_current = self.apply_filters(
                base_query, search_query, current_start_date, current_end_date, status
            )

            query_previous = self.apply_filters(
                base_query, search_query, previous_start_date, previous_end_date, status
            )

            total_orders_current = await session.scalar(select(query_current).count())
            fulfilled_orders_current = await session.scalar(
                select(
                    query_current.filter(
                        Order.order_status == OrderStatus.DELIVERED
                    ).count()
                )
            )
            ready_for_pickup_orders_current = await session.scalar(
                select(
                    query_current.filter(
                        Order.order_status == OrderStatus.READY_FOR_PICKUP
                    ).count()
                )
            )
            processing_orders_current = await session.scalar(
                select(
                    query_current.filter(
                        Order.order_status == OrderStatus.PROCESSING
                    ).count()
                )
            )

            total_orders_previous = await session.scalar(select(query_previous).count())
            fulfilled_orders_previous = await session.scalar(
                select(
                    query_previous.filter(
                        Order.order_status == OrderStatus.DELIVERED
                    ).count()
                )
            )
            ready_for_pickup_orders_previous = await session.scalar(
                select(
                    query_previous.filter(
                        Order.order_status == OrderStatus.READY_FOR_PICKUP
                    ).count()
                )
            )
            processing_orders_previous = await session.scalar(
                select(
                    query_previous.filter(
                        Order.order_status == OrderStatus.PROCESSING
                    ).count()
                )
            )

            total_orders_percentage_change = calculate_percentage_change(
                total_orders_current, total_orders_previous
            )
            fulfilled_orders_percentage_change = calculate_percentage_change(
                fulfilled_orders_current, fulfilled_orders_previous
            )
            ready_for_pickup_orders_percentage_change = calculate_percentage_change(
                ready_for_pickup_orders_current, ready_for_pickup_orders_previous
            )
            processing_orders_percentage_change = calculate_percentage_change(
                processing_orders_current, processing_orders_previous
            )

            offset = (page - 1) * page_size
            paginated_orders_result = await session.execute(
                select(query_current).offset(offset).limit(page_size)
            )
            paginated_orders = paginated_orders_result.scalars().all()

            return {
                "orders": paginated_orders,
                "current_page": page,
                "page_size": page_size,
                "total_orders": total_orders_current,
                "fulfilled_orders": fulfilled_orders_current,
                "ready_for_pickup_orders": ready_for_pickup_orders_current,
                "processing_orders": processing_orders_current,
                "total_orders_percentage_change": total_orders_percentage_change,
                "fulfilled_orders_percentage_change": fulfilled_orders_percentage_change,
                "ready_for_pickup_orders_percentage_change": ready_for_pickup_orders_percentage_change,
                "processing_orders_percentage_change": processing_orders_percentage_change,
                "total_pages": (total_orders_current + page_size - 1) // page_size,
            }

    def apply_filters(
        self,
        query,
        search_query,
        start_date_obj: Optional[datetime] = None,
        end_date_obj: Optional[datetime] = None,
        status: Optional[OrderStatus] = None,
    ):
        if search_query:
            query = (
                query.join(Order.order_inventories)
                .join(OrderDeviceAssignment.inventory)
                .filter(Inventory.device_name.ilike(f"%{search_query}%"))
            )

        if status:
            query = query.filter(Order.order_status == status)

        if start_date_obj:
            query = query.filter(cast(Order.created_at, Date) >= start_date_obj)

        if end_date_obj:
            query = query.filter(cast(Order.created_at, Date) <= end_date_obj)

        return query

    async def update_order_status(self, order_uuid: str, status: str):
        async with self.session_factory() as session:
            try:
                order_to_update = await session.scalar(
                    select(Order).filter_by(uuid=order_uuid)
                )

                if not order_to_update:
                    raise Exception("Order not found")

                order_to_update.order_status = status
                await session.commit()
                await session.refresh(order_to_update)

                result = await session.execute(
                    select(Order)
                    .filter_by(uuid=order_uuid)
                    .options(
                        joinedload(Order.order_inventories)
                        .joinedload(OrderDeviceAssignment.inventory)
                        .joinedload(Inventory.images),
                        joinedload(Order.order_shipping_address),
                    )
                )

                order = result.scalars().first()
                return order

            except Exception as e:
                await session.rollback()
                raise e
