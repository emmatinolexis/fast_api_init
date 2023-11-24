from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item


def get_all_alert_policies(db: Session):
    try:
        alert_policy = get_all_items(db, models.AlertPolicy)
        return alert_policy
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_policy(db: Session, alert_policy: schemas.AlertPolicy):
    try:
        alert_policy_data = {
            "policy_name": alert_policy.policy_name,
            "minimum_idle_time": alert_policy.minimum_idle_time,
            "alert_policy_type_uuid": alert_policy.alert_policy_type_uuid,
            "geofence_type": alert_policy.geofence_type,
            "geofence_location": alert_policy.geofence_location,
            # "maintenance_type_uuid": alert_policy.maintenance_type_uuid,
        }
        create_item(db, models.AlertPolicy, alert_policy_data)
        return alert_policy_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_policy(
    db: Session,
    alert_policy_uuid: str,
    model: models.AlertPolicy,
    updated_alert_policy: schemas.AlertPolicy,
):
    try:
        updated_alert_policy_data = {
            "policy_name": updated_alert_policy.policy_name,
            "minimum_idle_time": updated_alert_policy.minimum_idle_time,
            "alert_policy_type_uuid": updated_alert_policy.alert_policy_type_uuid,
            "geofence_type": updated_alert_policy.geofence_type,
            "geofence_location": updated_alert_policy.geofence_location,
            # "maintenance_type_uuid": updated_alert_policy.maintenance_type_uuid,
        }
        updated = update_item(db, alert_policy_uuid, model, updated_alert_policy_data)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_policy(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertPolicy, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
