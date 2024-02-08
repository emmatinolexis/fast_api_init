from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.device_schema import DevicePayload
from app.service.device_service import DeviceService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)
msg_prefix = "device"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_devices_handler(
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/get_user_devices/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_all_user_devices(
    user_uuid: str,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_devices_by_user_uuid(user_uuid))
    except Exception as e:
        msg = f"{messages.GET_FAILED}  {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_device_handler(
    payload: DevicePayload,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        device = service.add(payload)
        return send_data(device)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_device_handler(
    uuid: str,
    payload: DevicePayload,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        device = service.patch_by_uuid(uuid, payload)
        if device is None:
            return send_client_side_error(user_msg=messages.DEVICE_NOT_FOUND + uuid)
        return send_data(device)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_device_by_uuid_handler(
    uuid: str,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        device = service.get_by_uuid(uuid)
        if device is None:
            return send_client_side_error(user_msg=messages.DEVICE_NOT_FOUND + uuid)
        return send_data(device)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_device_by_uuid_handler(
    uuid: str,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
