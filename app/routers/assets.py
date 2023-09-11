from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.repository import create_asset_type
from app.database.repository import get_asset_type
from app.database.repository import update_asset_type
from app.database.repository import delete_asset_type

from .shared import get_db

router = APIRouter(
    prefix="/asset_types",
    tags=["asset type"],
)

@router.get("/", response_model=List[schemas.AssetType])
async def get_asset_type_handler(asset_type: Session = Depends(get_db)):
    return get_asset_type(asset_type)

@router.post("/", response_model=schemas.AssetType)
async def create_asset_type_handler(asset_type: schemas.AssetType, db: Session = Depends(get_db)):
    return create_asset_type(db, asset_type)

@router.put("/{asset_type_id}", response_model=schemas.AssetType)
async def update_asset_type_handler(asset_type_id: int, updated_asset_type: schemas.AssetType, db: Session = Depends(get_db)):
    updated_asset = update_asset_type(db, asset_type_id, updated_asset_type)
    if updated_asset is None:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return updated_asset

@router.delete("/{asset_type_id}", response_model=schemas.AssetType)
async def delete_asset_type_handler(asset_type_id: int, db: Session = Depends(get_db)):
    deleted_asset = delete_asset_type(db, asset_type_id)
    if deleted_asset is None:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return deleted_asset