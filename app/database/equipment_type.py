from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import create_item, delete_item, get_all_items, update_item

# CRUD functionalities for Equipment Type


def get_all_equipment_types(db: Session):
    try:
        equipment_type = get_all_items(db, models.EquipmentType)
        return equipment_type
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_equipment_type(db: Session, equipment_type: schemas.EquipmentTypeCreate):
    try:
        equipment_type_data = {
            "equipment_type_name": equipment_type.equipment_type_name,
            "status": equipment_type.status,
            "equipment_uuid": equipment_type.equipment_uuid,
        }
        create_item(db, models.EquipmentType, equipment_type_data)
        return equipment_type_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_equipment_type(
    db: Session,
    uuid: str,
    model: models.EquipmentType,
    updated_equipment_type: schemas.EquipmentType,
):
    try:
        updated_equipment_type_data = {
            "equipment_type_name": updated_equipment_type.equipment_type_name,
            "status": updated_equipment_type.status,
            "equipment_uuid": updated_equipment_type.equipment_uuid,
        }
        update_item(db, uuid, model, updated_equipment_type_data)
        return updated_equipment_type_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_equipment_type(db: Session, uuid: str):
    try:
        return delete_item(db, models.EquipmentType, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
