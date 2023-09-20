from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from app.database import schemas
from app.database.assets import create_asset
from app.database.assets import get_all_assets
from app.database.assets import update_asset
from app.database import models

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

@router.put("/{asset_id}", response_model=schemas.Asset)
async def update_asset_handler(asset_id: int, updated_asset_type: schemas.Asset, db: Session = Depends(get_db)):
    updated_asset = update_asset(db, asset_id, updated_asset_type)
    if updated_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return updated_asset

@router.delete("/{asset_id}", response_model=schemas.Asset)
async def delete_asset_handler(asset_id: int, db: Session = Depends(get_db)):
    deleted_asset = db.query(models.Asset).filter(cast(models.Asset.asset_id, String) == cast(asset_id, String)).first()
    if deleted_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    else:
         db.delete(deleted_asset)
         db.commit()
    return deleted_asset