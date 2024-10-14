from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.subscription import PaystackSubscriptionPayload
from app.service.subscription_service import SubscriptionService
from app.service.user_subscription_service import UserSubscriptionService
from app.util.utils import (
    allow_admins_only,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)
msg_prefix = "subscription"


@router.get("", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def paystack_subscriptions_handler(
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_paystack_subscriptions(page, page_size))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/toggle_status/{subscription_code}", response_class=ORJSONResponse)
@inject
async def toggle_subscription_status_handler(
    subscription_code: str,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.toggle_subscription_status(subscription_code))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{subscription_code}", response_class=ORJSONResponse)
@inject
async def paystack_subscription_handler(
    subscription_code: str,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_paystack_subscription(subscription_code))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/user/{user_email}", response_class=ORJSONResponse)
@inject
async def paystack_subscription_by_email_handler(
    user_email: str,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_paystack_subscription_by_email(user_email))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_paystack_subscription_handler(
    payload: PaystackSubscriptionPayload,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        subscription = service.create_paystack_subscription(payload)
        return send_data(subscription)

    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/webhook", response_class=ORJSONResponse)
@inject
async def paystack_subscription_webhook_handler(
    paystack_payload: dict,
    service: UserSubscriptionService = Depends(
        Provide[Container.user_subscription_service]
    ),
):
    try:
        subscription = service.create_user_subscription(paystack_payload)
        return send_info(subscription)

    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
