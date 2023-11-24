from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.alert_maintenance_types import (
    create_alert_maintenance_type,
    delete_alert_maintenance_type,
    get_all_alert_maintenance_types,
    update_alert_maintenance_type,
)

from .shared import get_db

# from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/alert_maintenance_types",
    tags=["alert_maintenance_types"],
)


@router.get("/", response_model=List[schemas.AlertMaintenanceType])
async def get_alert_maintenance_types_handler(
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_alert_maintenance_types(db)


@router.post("/create", response_model=None)
async def create_alert_maintenance_type_handler(
    alert_maintenance_type: schemas.AlertMaintenanceType,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_maintenance_type(
        db=db, alert_maintenance_type=alert_maintenance_type
    )


@router.put("/update/{uuid}", response_model=schemas.AlertMaintenanceType)
async def update_alert_maintenance_type_handler(
    uuid: str,
    updated_alert_maintenance_type: schemas.AlertMaintenanceType,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return update_alert_maintenance_type(
        db,
        uuid,
        model=models.AlertMaintenanceType,
        updated_alert_maintenance_type=updated_alert_maintenance_type,
    )


@router.delete("/delete/{uuid}", response_model=schemas.AlertMaintenanceType)
async def delete_alert_maintenance_type_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_alert_maintenance_type(db, uuid)
