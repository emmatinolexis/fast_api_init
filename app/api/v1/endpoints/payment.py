from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.payment_schema import PaymentPayload
from app.service.payment_service import PaymentService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)
msg_prefix = "payment"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_subscription_handler(
    service: PaymentService = Depends(Provide[Container.payment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_subscription_handler(
    payload: PaymentPayload,
    service: PaymentService = Depends(Provide[Container.payment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        payment = service.add(payload)
        return send_data(payment)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PAYMENT_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_subscription_handler(
    uuid: str,
    payload: PaymentPayload,
    service: PaymentService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        payment = service.patch_by_uuid(uuid, payload)
        if payment is None:
            return send_client_side_error(user_msg=messages.PAYMENT_NOT_FOUND + uuid)
        return send_data(payment)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_subscription_by_uuid_handler(
    uuid: str,
    service: PaymentPayload = Depends(Provide[Container.payment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PAYMENT_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
