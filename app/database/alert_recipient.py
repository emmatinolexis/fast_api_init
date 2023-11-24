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

# from app.utils.enums import AccountType


def get_all_alert_recipients(db: Session):
    try:
        recipients = get_all_items(db, models.AlertRecipient)
        return recipients
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_recipient(db: Session, recipients: schemas.AlertRecipient) -> bool:
    try:
        data = {
            "alert_policy_uuid": recipients.alert_policy_uuid,
            "phone_number": recipients.phone_number,
        }

        create_item(db, models.AlertRecipient, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_recipient(
    db: Session,
    alert_recipient_uuid: str,
    model: models.AlertRecipient,
    updated_alert_recipient: schemas.AlertRecipient,
):
    try:
        updated_alert_recipient_data = {
            "alert_policy_uuid": updated_alert_recipient.alert_policy_uuid,
            "phone_number": updated_alert_recipient.phone_number,
        }
        updated = update_item(
            db, alert_recipient_uuid, model, updated_alert_recipient_data
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_recipient(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertRecipient, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_alert_recipient_by_uuid(db: Session, uuid: str):
    try:
        recipient = get_item_by_id(db, model=models.AlertRecipient, uuid=uuid)
        return recipient
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
