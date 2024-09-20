from app.model.peripheral_devices import PeripheralDevice





def peripheral_device_transformer(device: PeripheralDevice):
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
        "building": {
            "building_uuid": str(device.building.uuid),
            "building_name": device.building.building_name,
            "longitude": device.building.longitude,
            "latitude": device.building.latitude,
        } if device.building else None,
    }
