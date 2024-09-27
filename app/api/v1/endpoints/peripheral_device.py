from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.core.exceptions import AuthError, BadRequestError
from app.model.user import User
from app.schema.peripheral_device_schema import (
    CreateGatewayDeviceConfiguration,
    CreateNodeConfiguration,
    CreatePeripheralDevice,
    GetDeviceConfiguration,
    LinkGasCylinderToDevice,
    UpdateDeviceConfigThreshold,
    UpdatePeripheralDevice,
)
from app.service.device_configuration_service import DeviceConfigurationService
from app.service.device_node_configuration_service import DeviceNodeConfigService
from app.service.gas_cylinder_service import GasCylinderService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.util.enums import AccountType, DeviceConfigurationVersion, DeviceType
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_data_with_info,
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
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
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


@router.patch("/link")
@inject
async def link_gas_cylinder_to_peripheral_device(
    payload: LinkGasCylinderToDevice,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = service.link_gas_cylinder_to_peripheral_device(
            current_user.uuid,
            payload,
        )
        return send_data_with_info(
            data=response,
            info=messages.UPDATE_SUCCESS + "peripheral device",
        )
    except BadRequestError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
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


@router.get("/configurations/all", response_class=ORJSONResponse)
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
    gas_cylinder_service: GasCylinderService = Depends(
        Provide[Container.gas_cylinder_service]
    ),
    current_user: User = Depends(get_current_app_service),
):
    try:
        peripheral_device = peripheral_device_service.get_devices_by_serial_number(
            payload.serial_number
        )
        if not peripheral_device:
            return send_client_side_error("Device not found")

        configuration = service.get_device_configuration(payload.device_type)

        if not configuration:
            return send_client_side_error("Configuration not found")

        if payload.device_type == DeviceConfigurationVersion.SG_PYROGAURDE_V1:
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
                            ", ".join(
                                configuration.configuration.get("physical_quantity")
                            )
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
                        "humthresh": configuration.configuration.get(
                            "humidity_threshold"
                        ),
                        "airqthresh": configuration.configuration.get(
                            "air_quality_threshold"
                        ),
                        "mlxvel": configuration.configuration.get(
                            "critical_mxl_velocity"
                        ),
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

        if payload.device_type == DeviceConfigurationVersion.SG_GGAURGEPRO_VI:
            gas_cylinder = gas_cylinder_service.get_cylinder_by_device_serial(
                payload.serial_number
            )

            if not gas_cylinder:
                return send_client_side_error(
                    "Gas cylinder not found for this serial number"
                )

            configuration_data = {
                "key": "NODECONF",
                "value": {
                    "devconf": {
                        "nodeid": peripheral_device.node_id,
                        "desc": configuration.configuration.get("description"),
                        "full_weight": gas_cylinder.cylinder_type.full_weight,
                        "empty_weight": gas_cylinder.cylinder_type.empty_weight,
                        "devloc": ""
                        if not peripheral_device.location
                        else peripheral_device.location,
                        "mcu": configuration.configuration.get("microprocessor_unit"),
                        "sensors": str(
                            ", ".join(configuration.configuration.get("sensors"))
                        ),
                        "phyqnty": str(
                            ", ".join(
                                configuration.configuration.get("physical_quantity")
                            )
                        ),
                    },
                    "opconf": {
                        "upint": configuration.configuration.get("update_interval"),
                        "batcutoff": configuration.configuration.get("battery_cutoff"),
                        "obstime": configuration.configuration.get("observation_time"),
                        "threshold_1": configuration.configuration.get("threshold_1"),
                        "threshold_2": configuration.configuration.get("threshold_2"),
                        "threshold_3": configuration.configuration.get("threshold_3"),
                    },
                },
            }
            return send_data(configuration_data)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{building_uuid}", response_class=ORJSONResponse)
@inject
async def update_peripheral_device_handler(
    building_uuid: str,
    payload: UpdatePeripheralDevice,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = service.update_peripheral_device(
            current_user.uuid, payload, building_uuid
        )
        return send_info(response)

    except BadRequestError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/user", response_class=ORJSONResponse)
@inject
async def get_peripheral_devices_by_user_handler(
    device_type: DeviceType = Query(None, description="device type"),
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.account_type == AccountType.INDIVIDUAL:
            devices = service.get_user_devices(
                user_uuid=current_user.uuid, device_type=device_type
            )
        else:
            devices = service.get_business_devices(
                business_profile_uuid=current_user.business_profile_uuid,
                device_type=device_type,
            )

        return send_data_with_info(info=messages.GET_SUCCESS + "devices", data=devices)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/building/{building_uuid}", response_class=ORJSONResponse)
@inject
async def get_peripheral_devices_by_building_handler(
    building_uuid: str,
    device_type: DeviceType = Query(None, description="device type"),
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:

        devices = service.get_building_devices(building_uuid, device_type)
        return send_data_with_info(info=messages.GET_SUCCESS + "devices", data=devices)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/update_threshold/{device_serial_number}", response_class=ORJSONResponse)
@inject
async def update_device_threshold_handler(
    device_serial_number: str,
    payload: UpdateDeviceConfigThreshold,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        data = service.update_device_threshold(
            device_serial_number, payload, current_user.uuid
        )
        return send_data_with_info(
            data=data,
            info=messages.UPDATE_SUCCESS + "device threshold",
        )
    except AuthError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/default/{peripheral_device_uuid}", response_class=ORJSONResponse)
@inject
async def set_peripheral_device_to_default_handler(
    peripheral_device_uuid: str,
    service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        data = service.set_device_configuration_to_default(peripheral_device_uuid)
        return send_data_with_info(data, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/toggle_alert_status/{peripheral_device_uuid}", response_class=ORJSONResponse)
@inject
async def update_sent_alert_status(
    peripheral_device_uuid: str,
    peripheral_service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        device = peripheral_service.get_device_by_peripheral_uuid(peripheral_device_uuid)

        if not device:
            return send_client_side_error(messages.PERIPHERAL_DEVICE_NOT_FOUND_MSG, messages.PERIPHERAL_DEVICE_NOT_FOUND_MSG)

        device_config = peripheral_service.get_device_conf_by_peripheral_uuid(peripheral_device_uuid)

        if not device_config:
            return send_client_side_error(messages.DEVICE_CONFIG_NOT_FOUND, messages.DEVICE_CONFIG_NOT_FOUND)

        device_update = peripheral_service.toggle_send_alert_status(peripheral_device_uuid)
        return send_data_with_info(device_update, messages.SUCCESS_MESSAGE)
    except AuthError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
