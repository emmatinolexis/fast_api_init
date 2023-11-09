from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item

# CRUD functionalities for Assets and AssetTypes


def get_all_assets(db: Session):
    try:
        return get_all_items(db, models.Asset)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")

def create_asset(db: Session, asset: schemas.Asset):
    try:
        asset_data = {
            "asset_name": asset.asset_name,
            "user_uuid": asset.user_uuid,
            "asset_status" : asset.asset_status,
            "asset_type_uuid": asset.asset_type_uuid,
            "vin_no": asset.vin_no,
            "equipment_type_uuid": asset.equipment_type_uuid,
            "marker_icon_uuid": asset.marker_icon_uuid,
            "marker_color": asset.marker_color
        }
        create_item(db, models.Asset, asset_data)
        return asset_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_asset(db: Session, uuid: str, updated_asset: schemas.Asset):
    try:
        updated_asset_data = {
            "asset_name": updated_asset.asset_name,
            "user_uuid": updated_asset.user_uuid,
            "asset_status" : updated_asset.asset_status,
            "asset_type_uuid": updated_asset.asset_type_uuid,
            "vin_no": updated_asset.vin_no,
            "equipment_type_uuid": updated_asset.equipment_type_uuid,
            "marker_icon_uuid":updated_asset.marker_icon_uuid,
            "marker_color": updated_asset.marker_color
        }
        update_item(db, uuid, updated_asset_data)
        return update_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_asset(db: Session, uuid: str):
    try:
        return delete_item(db, models.Asset, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_asset_type(db: Session):
    try:
        return get_all_items(db, models.AssetType)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_asset_type(db: Session, asset_type: schemas.AssetType):
    try:
        asset_type_data = {
            "asset_type_name": asset_type.asset_type_name,
            "description": asset_type.description,
            "icon_url": asset_type.icon_url,
            "status": asset_type.status,
        }
        create_item(db, models.AssetType, asset_type_data)
        return asset_type_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_asset_type(
    db: Session,
    uuid: str,
    model: models.AssetType,
    updated_asset_type: schemas.AssetType,
):
    # Prepare the data for the update
    try:
        updated_asset_type_data = {
            "asset_type_name": updated_asset_type.asset_type_name,
            "description": updated_asset_type.description,
            "icon_url": updated_asset_type.icon_url,
            "status": updated_asset_type.status,
        }
        # return updated_asset_type_data
        update_item(db, uuid, model, updated_asset_type_data)
        return updated_asset_type_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_asset_type(db: Session, uuid: str):
    try:
        return delete_item(db, models.AssetType, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
