from app.model.peripheral_devices import DeviceNodeConfig, PeripheralDevice
from app.repository.device_events_repository import DeviceEventRepository
from app.repository.device_node_configuration_repository import (
    DeviceNodeConfigRepository,
)
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.util.enums import PeripheralDeviceType


def pyro_node_config_transformer(device_node_config: DeviceNodeConfig):
    return {
        "ambient_temperature_threshold": device_node_config.ambient_temperature_threshold,
        "humidity_threshold": device_node_config.humidity_threshold,
        "target_temperature_threshold": device_node_config.target_temperature_threshold,
        "flammable_smoke_threshold": device_node_config.flammable_smoke_threshold,
    }


def gas_node_config_transformer(device_node_config: DeviceNodeConfig):
    return {
        "minimum_threshold": device_node_config.minimum_threshold,
    }


async def peripheral_device_transformer(
    device: PeripheralDevice,
    device_repo: PeripheralDeviceRepository,
    config_repo: DeviceNodeConfigRepository,
    device_event_repository: DeviceEventRepository,
    gas_cylinder_repo: GasCylinderRepository,
):
    device = await device_repo.read_by_uuid(device.uuid)

    # Initialize device_config and gas_cylinder_data
    device_config = None
    gas_cylinder_data = None

    # Retrieve and transform device configuration based on device type
    if device.device_type in [
        PeripheralDeviceType.PYROGUARD_NODE_DEVICE,
        PeripheralDeviceType.GAS_NODE_DEVICE,
    ]:
        config = await config_repo.get_device_node_config_by_device_uuid(device.uuid)
        measurement = {}

        if config:
            if device.device_type == PeripheralDeviceType.PYROGUARD_NODE_DEVICE:
                device_config = pyro_node_config_transformer(config)
            elif device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
                device_config = gas_node_config_transformer(config)

    # Fetch gas cylinder data only if the device type is GAS_NODE_DEVICE
    if device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
        cylinder = await gas_cylinder_repo.read_by_uuid(device.gas_cylinder_uuid)
        if cylinder:
            gas_cylinder_data = {"name": cylinder.cylinder_name, "uuid": cylinder.uuid}

    latest_event = await device_event_repository.get_device_latest_reading(
        device.node_id
    )

    if latest_event:
        if device.device_type == PeripheralDeviceType.PYROGUARD_NODE_DEVICE:
            ambient_temperature_threshold = {
                "value": latest_event.measurements[1].get("value"),
                "unit": latest_event.measurements[1].get("unit"),
            }

            measurement["ambient_temperature_threshold"] = ambient_temperature_threshold

            humidity_threshold = {
                "value": latest_event.measurements[2].get("value"),
                "unit": latest_event.measurements[2].get("unit"),
            }

            measurement["humidity_threshold"] = humidity_threshold

            target_temperature_threshold = {
                "value": latest_event.measurements[0].get("value"),
                "unit": latest_event.measurements[0].get("unit"),
            }

            measurement["target_temperature_threshold"] = target_temperature_threshold

            flammable_smoke_threshold = {
                "value": latest_event.measurements[3].get("value"),
                "unit": latest_event.measurements[3].get("unit"),
            }

            measurement["flammable_smoke_threshold"] = flammable_smoke_threshold

        if device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
            gas_level = {
                "value": latest_event.measurements[0].get("value"),
                "unit": latest_event.measurements[0].get("unit"),
            }

            measurement["gas_level"] = gas_level

    return {
        "uuid": str(device.uuid),
        "serial_number": device.serial_number,
        "node_id": str(device.node_id) if device.node_id else None,
        "status": device.status.name if device.status else None,
        "user_uuid": str(device.user_uuid) if device.user_uuid else None,
        "business_profile_uuid": (
            str(device.business_profile_uuid) if device.business_profile_uuid else None
        ),
        "building_uuid": str(device.building_uuid) if device.building_uuid else None,
        "location": device.location,
        "device_type": device.device_type.name if device.device_type else None,
        "device_configuration": device_config,
        # "send_alert_status": device.send_alert_status,
        "current_device_reading": measurement,
        "gas_cylinder_data": gas_cylinder_data,  # This is now safely initialized
    }
