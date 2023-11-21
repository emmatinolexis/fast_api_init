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


def get_all_alert_policy_types(db: Session):
    try:
        alert_policy_type = get_all_items(db, models.AlertPolicyType)
        return alert_policy_type
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_policy_type(db: Session, alert_policy_type: schemas.AlertPolicyType):
    try:
        alert_policy_types_data = {
            "name": alert_policy_type.name,
            "description": alert_policy_type.description,
            "status": alert_policy_type.status,
        }
        create_item(db, models.AlertPolicyType, alert_policy_types_data)
        return alert_policy_types_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_policy_type(
    db: Session,
    alert_policy_type_uuid: str,
    model: models.AlertPolicyType,
    updated_alert_policy_type: schemas.AlertPolicyType,
):
    try:
        updated_alert_policy_type_data = {
            "name": updated_alert_policy_type.name,
            "description": updated_alert_policy_type.description,
            "status": updated_alert_policy_type.status,
        }
        updated = update_item(
            db, alert_policy_type_uuid, model, updated_alert_policy_type_data
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_policy_type(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertPolicyType, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_alert_policy_types_by_uuid(db: Session, uuid: str):
    try:
        alert_policy_type = get_item_by_id(db, model=models.AlertPolicyType, uuid=uuid)
        return alert_policy_type
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
