from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user, get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.alert_policy_schema import AlertPolicyTypePayload
from app.service.alert_policy_type_service import AlertPolicyTypeService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
    allow_admins_only
)

router = APIRouter(
    prefix="/alert_policy_types",
    tags=["alert policy types"],
)
msg_prefix = "alert policy type"


@router.get("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_alert_policy_types_handler(
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user_with_permission("view_policy_type")),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_alert_policy_type_handler(
    payload: AlertPolicyTypePayload,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user_with_permission("create_policy_type")),
):
    try:
        alert_policy_type = service.add(payload)
        return send_data(alert_policy_type)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_alert_policy_type_handler(
    uuid: str,
    payload: AlertPolicyTypePayload,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user_with_permission("update_policy_type")),
):
    try:
        alert_policy_type = service.patch_by_uuid(uuid, payload)
        if alert_policy_type is None:
            return send_client_side_error(
                user_msg=messages.ALERT_POLICY_TYPE_NOT_FOUND + uuid
            )
        return send_data(alert_policy_type)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_alert_policy_types_by_uuid_handler(
    uuid: str,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user_with_permission("view_policy_type")),
):
    try:
        alert_policy_type = service.get_by_uuid(uuid)
        if alert_policy_type is None:
            return send_client_side_error(
                user_msg=messages.ALERT_POLICY_TYPE_NOT_FOUND + uuid
            )
        return send_data(alert_policy_type)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


# @router.delete("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
# @inject
# async def delete_alert_policy_type_by_uuid_handler(
#     uuid: str,
#     service: AlertPolicyTypeService = Depends(
#         Provide[Container.alert_policy_type_service]
#     ),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         service.remove_by_uuid(uuid)
#         return send_info(messages.DELETE_SUCCESS + msg_prefix)
#     except NotFoundError as e:
#         return send_client_side_error(
#             user_msg=messages.ALERT_POLICY_TYPE_NOT_FOUND + str(e.detail)
#         )
#     except Exception as e:
#         msg = messages.DELETE_FAILED + msg_prefix
#         return send_internal_server_error(user_msg=msg, error=e)
