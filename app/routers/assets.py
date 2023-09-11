from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.repository import (
    create_asset_type,
)

from .shared import get_db

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)
 
@router.post("/", response_model=schemas.AssetType)
async def create_asset_type_handler(asset_type: schemas.AssetType, db: Session = Depends(get_db)):
    
    return create_asset_type(db, asset_type)
