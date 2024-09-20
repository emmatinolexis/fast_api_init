from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestError
from app.model.user import User
from app.schema.peripheral_device_schema import (
    CreateGatewayDeviceConfiguration,
    CreatePeripheralDevice,
    UpdatePeripheralDevice,
)
from app.service.device_configuration_service import DeviceConfigurationService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.util.enums import DeviceType
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_info,
    send_internal_server_error,
)
from app.util.enums import AccountType,DeviceType

router = APIRouter(
    prefix="/peripheral_devices",
    tags=["peripheral_devices"],
)
msg_prefix = "peripheral_devices"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_peripheral_devices_handler(
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page, default is 10"),
    device_type: Optional[DeviceType] = Query(
        None,
        description="Filter by device type. Possible values: PYROGUARD_NODE_DEVICE, GATEWAY_DEVICE, GAS_DEVICE",
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter by serial_number or device_type"
    ),
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        devices = service.get_list(
            page=page, page_size=page_size, device_type=device_type, search=search
        )
        return send_data(devices)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_peripheral_devices_handler(
    payload: CreatePeripheralDevice,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.create_peripheral_device(payload)
        return send_info("Peripheral devices created successfully")
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/gateway_configuration", response_class=ORJSONResponse)
@inject
async def create_gateway_configuration_handler(
    payload: CreateGatewayDeviceConfiguration,
    service: DeviceConfigurationService = Depends(
        Provide[Container.device_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.create_gateway_configuration(payload)
        return send_info("Gateway Configuration created successfully")
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/configurations", response_class=ORJSONResponse)
@inject
async def get_all_device_configurations_handler(
    service: DeviceConfigurationService = Depends(
        Provide[Container.device_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{building_uuid}", response_class=ORJSONResponse)
@inject
async def update_peripheral_device_handler(
    building_uuid :str,
    payload: UpdatePeripheralDevice,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = service.update_peripheral_device(current_user.uuid, payload,building_uuid)
        return send_info(response)

    except BadRequestError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
    


@router.get("/user", response_class=ORJSONResponse)
@inject
async def get_peripheral_devices_by_user_handler(
    device_type:DeviceType = Query(None,description="device type"),
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.account_type == AccountType.INDIVIDUAL:
            devices = service.get_user_devices(user_uuid = current_user.uuid,device_type= device_type)
        else:
            devices = service.get_business_devices(
                user_uuid=current_user.uuid, business_profile_uuid=current_user.business_profile_uuid,device_type = device_type
            )
        
        return send_data_with_info(
            info=messages.GET_SUCCESS + "devices",
            data=devices
        )
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)



@router.get("/building/{building_uuid}",response_class=ORJSONResponse)
@inject
async def get_peripheral_devices_by_building_handler(
    building_uuid:str,
    device_type:DeviceType = Query(None,description="device type"),
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        devices = service.get_building_devices(building_uuid,device_type)
        return send_data_with_info(
            info=messages.GET_SUCCESS + "devices",
            data=devices
        )
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)