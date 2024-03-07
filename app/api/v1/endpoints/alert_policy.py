from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.alert_policy_schema import (
    AlertPolicyPayload,
    GeofenceAlertPolicyPayload,
)
from app.service.alert_policy_service import AlertPolicyService
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/alert_policies",
    tags=["alert policies"],
)
msg_prefix = "alert policy"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_alert_policies_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_alert_policies())
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_policies_by_user_handler(
    user_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_alert_policies_by_user(user_uuid))
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_policy_handler(
    payload: AlertPolicyPayload,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        alert_policy = service.create_alert_policy(payload, current_user.uuid)
        return send_data(alert_policy)
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/geofence", response_class=ORJSONResponse)
@inject
async def create_geofence_alert_policy_handler(
    payload: GeofenceAlertPolicyPayload,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        alert_policy = service.create_geofence_alert_policy(payload, current_user.uuid)
        return send_data(alert_policy)
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
