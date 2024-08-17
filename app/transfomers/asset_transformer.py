from app.model.asset import Asset


def asset_transformer(asset: Asset):
    return {
        "uuid": asset.uuid,
        "user_uuid": asset.user_uuid,
        "asset_type_uuid": asset.asset_type_uuid,
        "asset_name": asset.asset_name,
        "image_url": asset.image_url,
        "asset_status": asset.asset_status,
        "equipment_type_uuid": asset.equipment_type_uuid,
        "vin": asset.vin if asset.vin else None,
        "vehicle_license_no": asset.vehicle_license_no
        if asset.vehicle_license_no
        else None,
        "marker_color": asset.marker_color,
        "equipment_uuid": asset.equipment_uuid if asset.equipment_uuid else None,
        "serial_number": asset.serial_number if asset.serial_number else None,
        "make": asset.make if asset.make else None,
        "model": asset.model if asset.model else None,
    }
