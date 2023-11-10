from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.asset_location import (
    create_asset_location,
    delete_asset_location,
    get_all_asset_location,
    update_asset_location,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/asset_location",
    tags=["asset_location"],
)


@router.get("/", response_model=List[schemas.AssetLocation])
async def get_all_asset_location_handler(
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_asset_location(db)


@router.post("/create", response_model=schemas.AssetLocation)
async def create_asset_location_handler(
    asset_location: schemas.AssetLocation,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_asset_location(db, asset_location)


@router.put("/update/{uuid}", response_model=schemas.AssetLocation)
async def update_asset_location_handler(
    uuid: str,
    updated_asset_location: schemas.AssetLocation,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return update_asset_location(
        db,
        uuid,
        model=models.AssetLocation,
        updated_asset_location=updated_asset_location,
    )


@router.delete("/delete/{uuid}", response_model=schemas.AssetLocation)
async def delete_asset_location_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_asset_location(db, uuid)
