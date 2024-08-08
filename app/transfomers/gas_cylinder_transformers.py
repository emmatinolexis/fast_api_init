from app.model.gas_cylinders import GasCylinder


def gas_cylinder_transformer(gas_cylinder: GasCylinder):
    return {
        "uuid": gas_cylinder.uuid,
        "cylinder_name": gas_cylinder.cylinder_name,
        "status": gas_cylinder.status,
        "material_type": gas_cylinder.material_type,
        "user_uuid": gas_cylinder.user_uuid,
        "building_uuid": gas_cylinder.building_uuid,
        "gas_device_serial_number": gas_cylinder.gas_device_serial_number
        if gas_cylinder.gas_device_serial_number
        else None,
        "business_profile_uuid": gas_cylinder.business_profile_uuid
        if gas_cylinder.business_profile_uuid
        else None,
        "cylinder_type_uuid": gas_cylinder.cylinder_type_uuid,
    }
