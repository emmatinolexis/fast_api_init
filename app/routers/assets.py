from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.assets import create_asset
from app.database.assets import get_all_assets
from app.database.assets import update_asset
from app.database.assets import delete_asset

from .shared import get_db

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)

@router.get("/", response_model=List[schemas.Asset])
async def get_asset_handler(asset_type: Session = Depends(get_db)):
    return get_all_assets(asset_type)

@router.post("/", response_model=schemas.Asset)
async def create_asset_handler(asset_type: schemas.Asset, db: Session = Depends(get_db)):
    return create_asset(db, asset_type)

@router.put("/{asset_type_id}", response_model=schemas.Asset)
async def update_asset_handler(asset_type_id: int, updated_asset_type: schemas.Asset, db: Session = Depends(get_db)):
    updated_asset = update_asset(db, asset_type_id, updated_asset_type)
    if updated_asset is None:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return updated_asset

@router.delete("/{asset_type_id}", response_model=schemas.Asset)
async def delete_asset_handler(asset_type_id: int, db: Session = Depends(get_db)):
    deleted_asset = delete_asset(db, asset_type_id)
    if deleted_asset is None:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return deleted_asset