from app.model.gas_cylinders import GasDevice


def gas_device_transformer(gas_device: GasDevice):
    return {
        "uuid": gas_device.uuid,
        "device_name": gas_device.device_name,
        "serial_number": gas_device.serial_number,
        "status": gas_device.status,
        "user_uuid": gas_device.user_uuid,
        "business_profile_uuid": gas_device.business_profile_uuid
        if gas_device.business_profile_uuid
        else None,
        "building_uuid": gas_device.building_uuid if gas_device.building_uuid else None,
        "location": gas_device.location if gas_device.location else None,
        "device_type": gas_device.device_type,
        "created_at": gas_device.created_at,
        "updated_at": gas_device.updated_at,
    }
