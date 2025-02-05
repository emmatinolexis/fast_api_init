from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.device_schema import DeviceManufacturerPayload
from app.service.device_manufacturer_service import DeviceManufacturerService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/devices_manufacturers",
    tags=["device_manufacturers"],
)
msg_prefix = "device_manufacturer"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_device_manafacturers_handler(
    service: DeviceManufacturerService = Depends(
        Provide[Container.device_manufacturer_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(await service.get_list())
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/device_manufacturers", response_class=ORJSONResponse)
@inject
async def create_device_manufacturer_handler(
    payload: DeviceManufacturerPayload,
    service: DeviceManufacturerService = Depends(
        Provide[Container.device_manufacturer_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        manufacturer = await service.add(payload)
        return send_data(manufacturer)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_MANUFACTURER_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/device_manufacturers/{uuid}", response_class=ORJSONResponse)
@inject
async def update_device_manufacturer_handler(
    uuid: str,
    payload: DeviceManufacturerPayload,
    service: DeviceManufacturerService = Depends(
        Provide[Container.device_manufacturer_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        device = await service.patch_by_uuid(uuid, payload)
        if device is None:
            return send_client_side_error(
                user_msg=messages.DEVICE_MANUFACTURER_NOT_FOUND + uuid
            )
        return send_data(device)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/device_manufacturers/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_device_manufacturer_by_uuid_handler(
    uuid: str,
    service: DeviceManufacturerPayload = Depends(
        Provide[Container.device_manufacturer_service]
    ),
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
