from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.device_schema import DevicePayload, ImeiAssignPayload
from app.service.business_profile_service import BusinessProfileService
from app.service.device_service import DeviceService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)
from typing import Optional
from app.util.enums import DeviceStatus

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)
msg_prefix = "device"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_devices_handler(
    page: int = Query(1, ge=1, description="Page number, default is 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page, default is 10"),
    search_query: Optional[str] = Query(None, description="Search by manufacturer name"),
    status: Optional[DeviceStatus] = Query(
        None,
        description='Filter by active status'
    ), 
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        devices = service.get_all_devices(
            page=page, page_size=page_size, search_query=search_query,status=status
        )
        return send_data(devices)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/user_devices/{user_uuid}", response_class=ORJSONResponse)
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


@router.get("/business_devices/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_all_business_devices(
    business_uuid: str,
    service: DeviceService = Depends(Provide[Container.device_service]),
    business_service: BusinessProfileService = Depends(
        Provide[Container.business_profile_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        business = business_service.get_business_by_uuid(business_uuid)

        if business is None:
            return send_client_side_error(messages.BUSINESS_PROFILE_NOT_FOUND_MSG)
        return send_data(service.get_devices_by_business_uuid(business_uuid))
    except Exception as e:
        msg = f"{messages.GET_FAILED}  {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/third_party/device/{device_imei}/user", response_class=ORJSONResponse)
@inject
async def get_user_by_device_uuid(
    device_imei: str,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_app_service: User = Depends(get_current_app_service),
):
    try:
        return send_data(service.get_user_data_by_device_uuid(device_imei))
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
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


@router.post("/{device_uuid}/assign_imei", response_class=ORJSONResponse)
@inject
async def assign_imei_handler(
    device_uuid: str,
    payload: ImeiAssignPayload,
    service: DeviceService = Depends(Provide[Container.device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        device = service.assign_imei(device_uuid, payload.device_imei)
        return send_data(device)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
