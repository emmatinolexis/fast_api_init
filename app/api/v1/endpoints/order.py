from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.model.user import User
from app.schema.order_schema import OrderPayload, OrderStatus
from app.service.order_service import OrderService
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
        return send_data(order)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_orders_handler(
    service: OrderService = Depends(Provide[Container.order_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        orders = service.get_all_orders()
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
        order = service.update_order_status(order_uuid, order_status.order_status)
        return send_data(order)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
