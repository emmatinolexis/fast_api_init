from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.subscription import SubscriptionPayload, UpdateUserSubscriptionPayload
from app.service.plan_updgrade_service import PlanUpgradeService
from app.service.subscription_service import SubscriptionService
from app.util.utils import (
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


@router.get("", response_class=ORJSONResponse)
@inject
async def get_all_subscription_handler(
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=100, description="Items per page, default is 10"
    ),
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_subscriptions(page, page_size))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_subscription_handler(
    payload: SubscriptionPayload,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        subscription = service.add(payload)
        return send_data(subscription)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.SUBSCRIPTION_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_subscription_handler(
    uuid: str,
    payload: SubscriptionPayload,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        subscription = service.patch_by_uuid(uuid, payload)
        if subscription is None:
            return send_client_side_error(
                user_msg=messages.SUBSCRIPTION_NOT_FOUND + uuid
            )
        return send_data(subscription)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_subscription_by_uuid_handler(
    uuid: str,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.SUBSCRIPTION_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/user", response_class=ORJSONResponse)
@inject
async def update_user_subscription_handler(
    payload: UpdateUserSubscriptionPayload,
    service: PlanUpgradeService = Depends(Provide[Container.plan_upgrade_service]),
    # current_user: User = Depends(get_current_user),
):
    try:
        subscription = service.add(payload)
        return send_data(subscription)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.SUBSCRIPTION_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/subscription_upgrade", response_class=ORJSONResponse)
@inject
async def subscription_upgrade_handler(
    background_tasks: BackgroundTasks,
    service: SubscriptionService = Depends(Provide[Container.subscription_service]),
):
    try:
        service.subscriptions_upgrade(background_tasks)
        msg = "Subscription upgrade task added to background queue"
        return send_data(msg)
    except Exception as e:
        msg = "Failed to add subscription upgrade task to background queue"
        return send_internal_server_error(user_msg=msg, error=e)
