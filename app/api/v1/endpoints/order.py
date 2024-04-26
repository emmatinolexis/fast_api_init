from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.order_schema import OrderPayload
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
