from app.model.peripheral_devices import PeripheralDevice, DeviceNodeConfig
from app.util.enums import PeripheralDeviceType
from app.repository.device_node_configuration_repository import DeviceNodeConfigRepository
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository



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




def peripheral_device_transformer(
    device: PeripheralDevice, 
    device_repo: PeripheralDeviceRepository, 
    config_repo: DeviceNodeConfigRepository
):
    # Fetch the full device details with its configuration
    device = device_repo.read_by_uuid(device.uuid)

    print(device.device_type)
    
    # Initialize device_config
    device_config = None
    
    # Retrieve and transform device configuration based on device type
    if device.device_type in [PeripheralDeviceType.PYROGUARD_NODE_DEVICE, PeripheralDeviceType.GAS_NODE_DEVICE]:
        config = config_repo.get_device_node_config_by_device_uuid(device.uuid)
        
        if config:
            if device.device_type == PeripheralDeviceType.PYROGUARD_NODE_DEVICE:
                device_config = pyro_node_config_transformer(config)
            elif device.device_type == PeripheralDeviceType.GAS_NODE_DEVICE:
                device_config = gas_node_config_transformer(config)

    return {
        "uuid": str(device.uuid),
        "serial_number": device.serial_number,
        "node_id": str(device.node_id) if device.node_id else None,
        "status": device.status.name if device.status else None,
        "user_uuid": str(device.user_uuid) if device.user_uuid else None,
        "business_profile_uuid": str(device.business_profile_uuid) if device.business_profile_uuid else None,
        "building_uuid": str(device.building_uuid) if device.building_uuid else None,
        "location": device.location,
        "device_type": device.device_type.name if device.device_type else None,
        "device_configuration": device_config,
    }



