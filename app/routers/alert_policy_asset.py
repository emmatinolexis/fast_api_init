from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.alert_policy_asset import (
    create_alert_policy_asset,
    delete_alert_policy_asset,
    get_alert_policy_asset_by_uuid,
    get_all_alert_policy_assets,
    update_alert_policy_asset,
)
# from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/alert_policy_assetss",
    tags=["alert_policy_assets"],
)


@router.get("/", response_model=List[schemas.AlertPolicyAsset])
async def get_all_alert_policy_assets_handler(
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_alert_policy_assets(db)


@router.post("/create", response_model=schemas.AlertPolicyAsset)
async def create_alert_policy_asset_handler(
    alert_policy_asset: schemas.AlertPolicyAsset,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_policy_asset(db=db, alert_policy_asset=alert_policy_asset)


@router.put("/update/{uuid}", response_model=schemas.AlertPolicyAsset)
async def update_alert_policy_asset_handler(
    uuid: str,
    updated_alert_policy_asset: schemas.AlertPolicyAsset,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return update_alert_policy_asset(
        db,
        uuid,
        model=models.AlertPolicyAsset,
        updated_alert_policy_type=updated_alert_policy_asset,
    )


@router.get("/{uuid}", response_model=schemas.AlertPolicyAsset)
async def get_alert_policy_asset_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return get_alert_policy_asset_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.AlertPolicyAsset)
async def delete_alert_policy_asset_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_alert_policy_asset(db, uuid)
