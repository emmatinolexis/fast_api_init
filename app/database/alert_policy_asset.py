from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import (
    create_item,
    delete_item,
    get_all_items,
    get_item_by_id,
    update_item,
)


def get_all_alert_policy_assets(db: Session):
    try:
        alert_policy_assets = get_all_items(db, models.AlertPolicyAsset)
        return alert_policy_assets
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_policy_asset(
    db: Session, alert_policy_asset: schemas.AlertPolicyAsset
):
    try:
        alert_policy_assets_data = {
            "asset_uuid": alert_policy_asset.asset_uuid,
            "alert_policy_uuid": alert_policy_asset.alert_policy_uuid,
        }
        create_item(db, models.AlertPolicyAsset, alert_policy_assets_data)
        return alert_policy_assets_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_policy_asset(
    db: Session,
    alert_policy_asset_uuid: str,
    model: models.AlertPolicyAsset,
    updated_alert_policy_asset: schemas.AlertPolicyAsset,
):
    try:
        updated_alert_policy_asset_data = {
            "asset_uuid": updated_alert_policy_asset.asset_uuid,
            "alert_policy_uuid": updated_alert_policy_asset.alert_policy_uuid,
        }
        updated = update_item(
            db, alert_policy_asset_uuid, model, updated_alert_policy_asset_data
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_policy_asset(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertPolicyAsset, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_alert_policy_asset_by_uuid(db: Session, uuid: str):
    try:
        alert_policy_asset = get_item_by_id(
            db, model=models.AlertPolicyAsset, uuid=uuid
        )
        return alert_policy_asset
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
