from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.peripheral_device_schema import (
    CreateGatewayDeviceConfiguration,
    CreateNodeConfiguration,
    CreatePeripheralDevice,
    GetDeviceConfiguration,
)
from app.service.device_configuration_service import DeviceConfigurationService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

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


@router.post("/node_configuration", response_class=ORJSONResponse)
@inject
async def create_node_configuration_handler(
    payload: CreateNodeConfiguration,
    service: DeviceConfigurationService = Depends(
        Provide[Container.device_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.create_node_configuration(payload)
        return send_info("Node Configuration created successfully")
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


@router.post("/configurations", response_class=ORJSONResponse)
@inject
async def get_device_configurations_handler(
    payload: GetDeviceConfiguration,
    peripheral_device_service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    service: DeviceConfigurationService = Depends(
        Provide[Container.device_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        peripheral_device = peripheral_device_service.get_devices_by_serial_number(
            payload.serial_number
        )
        if not peripheral_device:
            return send_client_side_error("Device not found")

        configuration = service.get_device_configuration()

        if not configuration:
            return send_client_side_error("Configuration not found")

        configuration_data = {
            "key": "SG-PRYO-V1",
            "value": {
                "devconf": {
                    "nodeid": peripheral_device.node_id,
                    "desc": configuration.configuration.get("description"),
                    "devloc": ""
                    if not peripheral_device.location
                    else peripheral_device.location,
                    "mcu": configuration.configuration.get("microprocessor_unit"),
                    "sensors": str(
                        ", ".join(configuration.configuration.get("sensors"))
                    ),
                    "phyqnty": str(
                        ", ".join(configuration.configuration.get("physical_quantity"))
                    ),
                },
                "opconf": {
                    "upint": configuration.configuration.get("update_interval"),
                    "batcutoff": configuration.configuration.get("battery_cutoff"),
                    "obstime": configuration.configuration.get("observation_time"),
                    "ttmphresh": configuration.configuration.get(
                        "target_temperature_threshold"
                    ),
                    "atmpthresh": configuration.configuration.get(
                        "ambient_temperature_threshold"
                    ),
                    "humthresh": configuration.configuration.get("humidity_threshold"),
                    "airqthresh": configuration.configuration.get(
                        "air_quality_threshold"
                    ),
                    "mlxvel": configuration.configuration.get("critical_mxl_velocity"),
                    "atvel": configuration.configuration.get(
                        "critical_ambient_temperature"
                    ),
                    "humvel": configuration.configuration.get(
                        "critical_humidity_velocity"
                    ),
                    "mqvel": configuration.configuration.get(
                        "critical_air_quality_velocity"
                    ),
                    "mlxaccel": configuration.configuration.get(
                        "critical_mxl_acceleration"
                    ),
                    "atmpaccel": configuration.configuration.get(
                        "critical_ambient_temperature_acceleration"
                    ),
                    "hunaccel": configuration.configuration.get(
                        "critical_humidity_acceleration"
                    ),
                    "mqaccel": configuration.configuration.get(
                        "critical_air_quality_acceleration"
                    ),
                },
            },
        }
        return send_data(configuration_data)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
