from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.assets import (
    create_asset_type,
    delete_asset_type,
    get_asset_type,
    update_asset_type,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/asset_types",
    tags=["asset_types"],
)


@router.get("/", response_model=List[schemas.AssetType])
async def get_all_asset_type_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_asset_type(db)


@router.post("/create", response_model=schemas.AssetType)
async def create_asset_type_handler(
    asset_type: schemas.AssetType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_asset_type(db, asset_type)


@router.put("/update/{uuid}", response_model=schemas.AssetType)
async def update_asset_type_handler(
    uuid: str,
    updated_asset_type: schemas.AssetType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_asset_type(
        db, uuid, model=models.AssetType, updated_asset_type=updated_asset_type
    )


@router.delete("/delete/{uuid}", response_model=schemas.AssetType)
async def delete_asset_type_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_asset_type(db, uuid)
