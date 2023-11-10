from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas

from app.database.assets import create_asset, delete_asset, get_all_assets, update_asset
from app.utils.auth import get_current_user


from .shared import get_db

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.get("/", response_model=List[schemas.Asset])
async def get_asset_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_assets(db)


@router.post("/create", response_model=schemas.AssetCreate)
async def create_asset_handler(
    asset: schemas.Asset,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_asset(db, asset)


@router.put("/update/{uuid}", response_model=None)
async def update_asset_handler(
    uuid: str,
    updated_asset: schemas.Asset,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    # return updated_asset
    return update_asset(db=db,uuid=uuid,model=models.Asset,updated_asset=updated_asset)


@router.delete("/delete/{uuid}", response_model=schemas.Asset)
async def delete_asset_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_asset(db, uuid)
