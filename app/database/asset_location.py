from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item

# CRUD functionalities for Asset Location


def get_all_asset_location(db: Session):
    try:
        locations = get_all_items(db, models.AssetLocation)
        return locations
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_asset_location(db: Session, asset_location: schemas.AssetLocation):
    try:
        asset_location_data = {
            "asset_uuid": asset_location.asset_uuid,
            "longitude": asset_location.longitude,
            "latitude": asset_location.latitude,
        }
        create_item(db, models.AssetLocation, asset_location_data)
        return asset_location_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_asset_location(
    db: Session,
    uuid: str,
    model: models.Asset,
    updated_asset_location: schemas.AssetLocation,
):
    try:
        updated_asset_location_data = {
            "asset_uuid": updated_asset_location.asset_uuid,
            "longitude": updated_asset_location.longitude,
            "latitude": updated_asset_location.latitude,
        }
        update_item(db, uuid, model, updated_asset_location_data)
        return updated_asset_location_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_asset_location(db: Session, uuid: str):
    try:
        return delete_item(db, models.AssetLocation, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
