from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.equipments import (
    create_equipment,
    delete_equipment,
    get_all_equipments,
    update_equipment,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/equipments",
    tags=["equipments"],
)


@router.get("/", response_model=list[schemas.EquipmentFetch])
async def get_all_equipments_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_equipments(db)


@router.post("/create", response_model=schemas.Equipment)
async def create_equipment_handler(
    equipment: schemas.Equipment,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_equipment(db, equipment)


@router.put("/update/{uuid}", response_model=schemas.Equipment)
async def update_equipment_handler(
    uuid: str,
    updated_equipment: schemas.Equipment,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_equipment(
        db=db,
        uuid=uuid,
        model=models.Equipment,
        updated_equipment=updated_equipment,
    )


@router.delete("/delete/{uuid}", response_model=schemas.Equipment)
async def delete_equipment_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_equipment(db, uuid)
