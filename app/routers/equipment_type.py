from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.equipment_type import (
    create_equipment_type,
    delete_equipment_type,
    get_all_equipment_types,
    update_equipment_type,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/equipment_types",
    tags=["equipment_types"],
)


@router.get("/", response_model=None)
async def get_all_equipment_types_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_equipment_types(db)


@router.post("/create", response_model=None)
async def create_equipment_type_handler(
    equipment_type: schemas.EquipmentType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_equipment_type(db, equipment_type)


@router.put("/update/{uuid}", response_model=None)
async def update_equipment_type_handler(
    uuid: str,
    updated_equipment_type: schemas.EquipmentType,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_equipment_type(
        db=db,
        uuid=uuid,
        model=models.EquipmentType,
        updated_equipment_type=updated_equipment_type,
    )


@router.delete("/delete/{uuid}", response_model=None)
async def delete_equipment_type(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_equipment_type(db, uuid)
