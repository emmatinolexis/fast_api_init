import logging

import requests
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.settings import settings
from app.model.user import User
from app.schema.subscription import PaystackSubscriptionPayload
from app.service.subscription_service import SubscriptionService
from app.service.user_service import UserService
from app.service.user_subscription_service import UserSubscriptionService
from app.util.enums import PaymentTypes
from app.util.utils import (
    allow_admins_only,
    send_client_side_error,
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


@router.get("/payments", response_class=ORJSONResponse)
@inject
async def get_all_paystack_payment_handler(
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_paystack_payments())
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
    service: UserSubscriptionService = Depends(
        Provide[Container.user_subscription_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_email_address(payload.email)

        if not user:
            return send_client_side_error(messages.USER_NOT_FOUND_MSG)

        paystack_plan = requests.get(
            settings.PAYSTACK_PLAN_URL + f"/{payload.plan}",
            headers=settings.PAYSTACK_HEADERS,
        )

        if paystack_plan.json().get("status"):
            payload_data = {
                "plan": payload.plan,
                "email": payload.email,
                "amount": payload.amount,
                "callback_url": payload.callback_url,
                "metadata": {
                    "business_profile_uuid": str(user.business_profile_uuid),
                    "payment_type": PaymentTypes.SUBSCRIPTION_PAYMENT,
                },
            }

            existing_subscription = service.get_subscription_by_business_uuid(
                user.business_profile_uuid, payload_data.get("plan")
            )

            if existing_subscription:
                return send_client_side_error(messages.SUBSCRIPTION_ALREADY_EXISTS)

            # create a new subscription
            subscription = service.create_paystack_subscription(
                payload_data, paystack_plan.json()["data"], user.business_profile_uuid
            )
            return send_data(subscription)

        else:
            return send_client_side_error(paystack_plan.json().get("message"))

        # package_to_update = service.get_subscription_by_email(payload_data.get("email"))

        # if package_to_update:
        #     # update subscription
        #     subscription = service.create_paystack_subscription(
        #         payload_data, user.business_profile_uuid, update_subscription=True
        #     )
        #     return send_data(subscription)
        # else:
        #     # create a new subscription
        #     subscription = service.create_paystack_subscription(
        #         payload_data, user.business_profile_uuid
        #     )
        #     return send_data(subscription)

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
        event_type = paystack_payload["event"]
        if event_type == "subscription.create":
            # check if subscription exist
            subscription_code = paystack_payload["data"]["subscription_code"]

            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                headers=settings.PAYSTACK_HEADERS,
            )
            subscription_data = paystack_subscription.json()

            if not subscription_data["status"]:
                logging.info(
                    subscription_data["message"]
                    + f" Subscription code: {subscription_code}"
                )
                return send_client_side_error(subscription_data["message"])

        if event_type == "charge.success":
            # validate payment
            payment_reference = paystack_payload["data"]["reference"]
            payment = requests.get(
                settings.PAYSTACK_PAYMENT_VERIFICATION_URL + f"/{payment_reference}",
                headers=settings.PAYSTACK_HEADERS,
            )
            payment_data = payment.json()

            if not payment_data["status"]:
                logging.info(payment_data["message"])
                return send_client_side_error(
                    payment_data["message"] + f" Transaction code : {payment_reference}"
                )

        subscription = service.create_user_subscription(paystack_payload)
        return send_info(subscription)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        logging.error(e)
        return send_internal_server_error(user_msg=msg, error=e)
