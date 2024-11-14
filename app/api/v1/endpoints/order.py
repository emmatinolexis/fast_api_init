from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
import logging
from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.model.user import User
from app.schema.order_schema import OrderPayload
from app.service.order_service import OrderService
from app.util.enums import OrderStatus
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/order",
    tags=["order"],
)
msg_prefix = "order"


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_order_handler(
    payload: OrderPayload,
    service: OrderService = Depends(Provide[Container.order_service]),
):
    try:
        order = service.create_order(payload)
        logging.info(f"Order created: {order}")
        return send_data(order)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_orders_handler(
    page: int = Query(1, ge=1, description="Page number, default is 1"),
    page_size: int = Query(
        10, ge=1, le=100, description="Items per page, default is 10"
    ),
    search_query: str = Query(None, description="Search by device name"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    start_date: str = Query(
        None, description="Filter orders from this date (YYYY-MM-DD)"
    ),
    end_date: str = Query(
        None, description="Filter orders up to this date (YYYY-MM-DD)"
    ),
    service: OrderService = Depends(Provide[Container.order_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        orders = service.get_all_orders(
            page=page,
            page_size=page_size,
            search_query=search_query,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )
        return send_data(orders)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{order_uuid}/status", response_class=ORJSONResponse)
@inject
async def update_status_to_ready_for_pick_handler(
    order_uuid: str,
    service: OrderService = Depends(Provide[Container.order_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        order = service.update_order_status_to_ready(order_uuid)
        logging.info(f"Role status updated: {order}")
        return order
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{order_uuid}/order_status_rtd", response_class=ORJSONResponse)
@inject
async def rtd_update_status_handler(
    order_uuid: str,
    order_status: OrderStatus,
    service: OrderService = Depends(Provide[Container.order_service]),
    current_user: User = Depends(get_current_app_service),
):
    try:
        order = service.update_order_status(order_uuid, order_status)
        logging.info(f"Role status updated: {order}")
        return send_data(order)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
