from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item

# CRUD functionalities for Equipment


def get_all_equipments(db: Session):
    try:
        equipment = get_all_items(db, models.Equipment)
        return equipment
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_equipment(db: Session, equipment: schemas.Equipment):
    try:
        equipment_data = {
            "name": equipment.name,
            "status": equipment.status,
        }
        create_item(db, models.Equipment, equipment_data)
        return equipment_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_equipment(
    db: Session,
    uuid: str,
    model: models.Equipment,
    updated_equipment: schemas.Equipment,
):
    try:
        updated_equipment_data = {
            "name": updated_equipment.name,
            "status": updated_equipment.status,
        }
        update_item(db, uuid, model, updated_equipment_data)
        return updated_equipment_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_equipment(db: Session, uuid: str):
    try:
        return delete_item(db, models.Equipment, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
