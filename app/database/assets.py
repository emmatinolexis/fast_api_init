from sqlalchemy.orm import Session
from . import models, schemas

from .helpers import get_all_items
from .helpers import create_item
from .helpers import update_item
from .helpers import delete_item

def get_all_assets(db: Session):
    return get_all_items(db, models.Asset)

def create_asset(db: Session, asset: schemas.Asset):
    asset_data = {
        "asset_name": asset.asset_name,
        "asset_type_id": asset.asset_type_id,
        "asset_status": asset.asset_status,
        "customer_id": asset.customer_id
    }
    return create_item(db, models.Asset, asset_data)

def update_asset(db: Session, asset_id: int, updated_asset: schemas.Asset):
    updated_asset_data = {
        "asset_name": updated_asset.asset_name,
        "asset_type_id": updated_asset.asset_type_id,
        "asset_status": updated_asset.asset_status,
        "customer_id": updated_asset.customer_id
    }
    return update_item(db, models.Asset, asset_id, updated_asset_data)

def delete_asset(db: Session, asset_id: int):
    return delete_item(db, models.Asset, asset_id)

def get_asset_type(db: Session):
    return get_all_items(db, models.AssetType)
