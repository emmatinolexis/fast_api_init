from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.subscription import PaystackSubscriptionPayload
from app.service.subscription_service import SubscriptionService
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)
msg_prefix = "subscription"


@router.get("", response_class=ORJSONResponse)
@inject
async def paystack_subscriptions_handler(
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_paystack_subscriptions())
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
