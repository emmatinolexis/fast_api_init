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


def get_all_alert_policy_notifications(db: Session):
    try:
        alert_policy_notification = get_all_items(db, models.AlertPolicyNotification)
        return alert_policy_notification
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_policy_notification(
    db: Session, alert_policy_notification: schemas.AlertPolicyNotification
):
    try:
        alert_policy_notification_data = {
            "alert_policy_uuid": alert_policy_notification.alert_policy_uuid,
            "alert_notification_type": alert_policy_notification.alert_notification_type,
        }
        create_item(db, models.AlertPolicyNotification, alert_policy_notification_data)
        return alert_policy_notification_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_policy_notification(
    db: Session,
    alert_policy_notification_uuid: str,
    model: models.AlertPolicyNotification,
    updated_alert_policy_notification: schemas.AlertPolicyNotification,
):
    try:
        updated_alert_policy_notification_data = {
            "alert_policy_uuid": updated_alert_policy_notification.alert_policy_uuid,
            "alert_notification_type": updated_alert_policy_notification.alert_notification_type,
        }
        updated = update_item(
            db,
            alert_policy_notification_uuid,
            model,
            updated_alert_policy_notification_data,
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_policy_notification(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertPolicyNotification, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_alert_policy_notification_by_uuid(db: Session, uuid: str):
    try:
        alert_policy_notification = get_item_by_id(
            db, model=models.AlertPolicyNotification, uuid=uuid
        )
        return alert_policy_notification
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
