from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.alert_policy_type import (
    create_alert_policy_type,
    delete_alert_policy_type,
    get_alert_policy_types_by_uuid,
    get_all_alert_policy_types,
    update_alert_policy_type,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/alert_policy_types",
    tags=["alert_policy_types"],
)


@router.get("/", response_model=List[schemas.AlertPolicyTypeFetch])
async def get_alert_policy_types_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_alert_policy_types(db)


@router.post("/create", response_model=None)
async def create_alert_policy_type_handler(
    alert_policy_type: schemas.AlertPolicyType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_policy_type(db=db, alert_policy_type=alert_policy_type)


@router.put("/update/{uuid}", response_model=schemas.AlertPolicyType)
async def update_alert_policy_type_handler(
    uuid: str,
    updated_alert_policy_type: schemas.AlertPolicyType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_alert_policy_type(
        db,
        uuid,
        model=models.AlertPolicyType,
        updated_alert_policy_type=updated_alert_policy_type,
    )


@router.get("/{uuid}", response_model=schemas.AlertPolicyType)
async def get_alert_policy_types_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return get_alert_policy_types_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.AlertPolicyType)
async def delete_alert_policy_type_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_alert_policy_type(db, uuid)
