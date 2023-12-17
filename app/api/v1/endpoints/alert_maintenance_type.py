from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.asset_schema import AlertMaintenanceTypePayload
from app.service.alert_maintenance_type_service import AlertMaintenanceTypeService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/alert_maintenance_types",
    tags=["alert maintenance types"],
)
msg_prefix = "alert maintenance type"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_alert_maintenance_types_handler(
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_maintenance_type_handler(
    payload: AlertMaintenanceTypePayload,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        alert_maintenance_type = service.add(payload)
        return send_data(alert_maintenance_type)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_alert_maintenance_type_handler(
    uuid: str,
    payload: AlertMaintenanceTypePayload,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        alert_maintenance_type = service.patch_by_uuid(uuid, payload)
        if alert_maintenance_type is None:
            return send_client_side_error(
                user_msg=messages.ALERT_MAINTENANCE_TYPE_NOT_FOUND + uuid
            )
        return send_data(alert_maintenance_type)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_alert_maintenance_type_by_uuid_handler(
    uuid: str,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.ALERT_MAINTENANCE_TYPE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
