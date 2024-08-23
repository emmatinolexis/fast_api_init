from app.model.buildings import Building


def building_transformer(building: Building):
    return {
        "uuid": building.uuid,
        "building_name": building.building_name,
        "longitude": building.longitude,
        "latitude": building.latitude,
        "image_url": building.image_url,
        "status": building.status,
        "business_profile_uuid": building.business_profile_uuid
        if building.business_profile_uuid
        else None,
        "user_uuid": building.user_uuid,
        "created_at": building.created_at,
        "updated_at": building.updated_at,
    }
