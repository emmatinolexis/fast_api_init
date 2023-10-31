from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import APIRouter,Depends,HTTPException
from .helpers import get_all_items
from .helpers import create_item
from .helpers import update_item
from .helpers import delete_item

#CRUD functionalities for Assets and AssetTypes

def get_all_assets(db: Session):
    return get_all_items(db, models.Asset)

def create_asset(db: Session, asset: schemas.Asset):
    asset_data = {
        "asset_name": asset.asset_name,
        "asset_id": asset.asset_id,
        "asset_status": asset.asset_status,
        "vin_no": asset.user_id
    }
    return create_item(db, models.Asset, asset_data)

def update_asset(db: Session, asset_id: int, updated_asset: schemas.Asset):
    updated_asset_data = {
        "asset_name": updated_asset.asset_name,
        "asset_id": updated_asset.asset_id,
        "asset_status": updated_asset.asset_status,
        "user_id": updated_asset.user_id
    }
    return update_item(db, asset_id, updated_asset_data)

def create_asset_type(db: Session, asset_type: schemas.AssetType):
    asset_type_data = {
        "asset_type_name": asset_type.asset_type_name,
        "description": asset_type.description,
        "icon_url": asset_type.icon_url,
        "status": asset_type.status
    }
    return create_item(db, models.AssetType, asset_type_data)

# def update_asset_type(db: Session,uuid:str,model:models.AssetType, asset_type: schemas.AssetType):
    updated_asset_type_data = {
        "asset_type_name": asset_type.asset_type_name,
        "description": asset_type.description,
        "icon_url": asset_type.icon_url,
        "status": asset_type.status
    }
    updated= update_asset_type(db, uuid, model,updated_asset_type_data)
    if updated:
        return updated_asset_type_data
    raise HTTPException(status_code=404, detail="Error updating asset type ")

def update_asset_type(db: Session, uuid: str, model: models.AssetType, asset_type: schemas.AssetType):
    # Prepare the data for the update
    updated_asset_type_data = {
        "asset_type_name": asset_type.asset_type_name,
        "description": asset_type.description,
        "icon_url": asset_type.icon_url,
        "status": asset_type.status
    }   

def delete_asset(db: Session, asset_id: int):
    return delete_item(db, models.Asset, asset_id)

def get_asset_type(db: Session):
    return get_all_items(db, models.AssetType)
