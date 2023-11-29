from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item


def get_all_alert_policies(db: Session):
    try:
        db_alert_policies = get_all_items(db, models.AlertPolicy)

        alert_policies = []

        for alert in db_alert_policies:
            alert_reciepients = (
                db.query(models.AlertNotificationAssignment)
                .filter(
                    models.AlertNotificationAssignment.alert_policy_uuid == alert.uuid
                )
                .all()
            )
            recipients = [row.reciepient for row in alert_reciepients]

            alert_notification_types = (
                db.query(models.AlertPolicyNotificationTypeAssignment)
                .filter(
                    models.AlertPolicyNotificationTypeAssignment.alert_policy_uuid
                    == alert.uuid
                )
                .all()
            )
            alert_notification_types = [
                row.alert_notification_type for row in alert_notification_types
            ]

            alert_assets = (
                db.query(models.Asset)
                .join(
                    models.AlertPolicyAssetAssignment,
                    models.AlertPolicyAssetAssignment.asset_uuid == models.Asset.uuid,
                )
                .filter(
                    models.AlertPolicyAssetAssignment.alert_policy_uuid == alert.uuid
                )
                .all()
            )
            alert_assets = [row.asset_name for row in alert_assets]

            alert_data = {
                "policy_name": alert.policy_name,
                "geofence_location_name": alert.geofence_location_name,
                "geofence_type": alert.geofence_type,
                "minimum_idle_time": alert.minimum_idle_time,
                "maintenance_alert_schedule": alert.maintenance_alert_schedule,
                "alert_policy_type": alert.alert_policy_type.name,
                "maintenance_alert_type": alert.maintenance_alert_type.name,
                "alert_reciepients": recipients,
                "alert_notification_types": alert_notification_types,
                "alert_assets": alert_assets,
            }

            alert_policies.append({"alert_policy": alert_data})
        return alert_policies
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_policy(db: Session, alert_policy: schemas.AlertPolicy):
    try:
        # create policy
        alert_policy_data = {
            "policy_name": alert_policy.policy_name,
            "alert_policy_type_uuid": alert_policy.alert_policy_type_uuid,
            "geofence_type": alert_policy.geofence_type,
            "geofence_location_name": alert_policy.geofence_location_name,
            "minimum_idle_time": alert_policy.minimum_idle_time,
            "maintenance_alert_schedule": alert_policy.maintenance_alert_schedule,
            "maintenance_alert_type_uuid": alert_policy.maintenance_alert_policy_type_uuid,
        }

        created_policy = create_item(db, models.AlertPolicy, alert_policy_data)
        # return created_policy

        # create alert reciepients
        for item in alert_policy.alert_reciepients:
            alert_reciepients_data = {
                "alert_policy_uuid": created_policy.uuid,
                "reciepient": item,
            }
            create_item(db, models.AlertNotificationAssignment, alert_reciepients_data)

        # create alert types
        for item in alert_policy.alert_types:
            alert_types_data = {
                "alert_policy_uuid": created_policy.uuid,
                "alert_notification_type": item,
            }
            create_item(
                db, models.AlertPolicyNotificationTypeAssignment, alert_types_data
            )

        # create alert assets
        for item in alert_policy.alert_assets:
            alert_assets_data = {
                "alert_policy_uuid": created_policy.uuid,
                "asset_uuid": item,
            }
            create_item(db, models.AlertPolicyAssetAssignment, alert_assets_data)

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
