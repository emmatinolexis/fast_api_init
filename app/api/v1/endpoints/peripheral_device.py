from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.peripheral_device_schema import (
    CreateGatewayDeviceConfiguration,
    CreatePeripheralDevice,
    UpdatePeripheralDevice
)
from app.service.device_configuration_service import DeviceConfigurationService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.util.utils import (
    send_data,
    send_info,
    send_internal_server_error,
    send_client_side_error,
    send_data_with_info
)
from app.core.exceptions import BadRequestError

router = APIRouter(
    prefix="/peripheral_devices",
    tags=["peripheral_devices"],
)
msg_prefix = "peripheral_devices"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_peripheral_devices_handler(
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
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
    


@router.patch("/{building_uuid}",response_class=ORJSONResponse)
@inject
async def update_peripheral_device_handler(
    payload : UpdatePeripheralDevice,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = service.update_peripheral_device(current_user.uuid,payload)
        return send_info(
            response
        )
        
    except BadRequestError as e:
        return send_client_side_error(
            user_msg=e.detail
        )
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
