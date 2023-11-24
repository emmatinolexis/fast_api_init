from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.alert_policy_notifications import (
    create_alert_policy_notification,
    delete_alert_policy_notification,
    get_alert_policy_notification_by_uuid,
    get_all_alert_policy_notifications,
    update_alert_policy_notification,
)
# from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/alert_policy_notifications",
    tags=["alert_policy_notifications"],
)


@router.get("/", response_model=List[schemas.AlertPolicyNotification])
async def get_alert_policy_notifications_handler(
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_alert_policy_notifications(db)


@router.post("/create", response_model=None)
async def create_alert_policy_notification_handler(
    alert_policy_notification: schemas.AlertPolicyNotification,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_policy_notification(
        db=db, alert_policy_notification=alert_policy_notification
    )


@router.put("/update/{uuid}", response_model=schemas.AlertPolicyNotification)
async def update_alert_policy_notification_handler(
    uuid: str,
    updated_alert_policy_notification: schemas.AlertPolicyNotification,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return update_alert_policy_notification(
        db,
        uuid,
        model=models.AlertPolicyNotification,
        updated_alert_policy_notification=updated_alert_policy_notification,
    )


@router.get("/{uuid}", response_model=schemas.AlertPolicyNotification)
async def get_alert_policy_notifications_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return get_alert_policy_notification_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.AlertPolicyNotification)
async def delete_alert_policy_notification_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_alert_policy_notification(db, uuid)
