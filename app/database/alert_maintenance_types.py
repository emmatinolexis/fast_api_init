from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item


def get_all_alert_maintenance_types(db: Session):
    try:
        alert_maintenance_type = get_all_items(db, models.AlertMaintenanceType)
        return alert_maintenance_type
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_alert_maintenance_type(
    db: Session, alert_maintenance_type: schemas.AlertMaintenanceType
):
    try:
        alert_maintenance_types_data = {
            "name": alert_maintenance_type.name,
            "status": alert_maintenance_type.status,
        }
        create_item(db, models.AlertMaintenanceType, alert_maintenance_types_data)
        return alert_maintenance_types_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_alert_maintenance_type(
    db: Session,
    alert_maintenance_type_uuid: str,
    model: models.AlertMaintenanceType,
    updated_alert_maintenance_type: schemas.AlertMaintenanceType,
):
    try:
        updated_alert_maintenance_type_data = {
            "name": updated_alert_maintenance_type.name,
            "status": updated_alert_maintenance_type.status,
        }
        updated = update_item(
            db, alert_maintenance_type_uuid, model, updated_alert_maintenance_type_data
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_alert_maintenance_type(db: Session, uuid: str):
    try:
        return delete_item(db, models.AlertMaintenanceType, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
