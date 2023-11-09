from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import (
    create_item,
    delete_item,
    get_all_items,
    get_item_by_id,
    update_item,
)

# CRUD functionalities for Assets


def get_all_marker_icons(db: Session):
    try:
        icons = get_all_items(db, models.MarkerIcon)
        return icons
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_marker_icon(db: Session, icon: schemas.MarkerIcon):
    try:
        icon_data = {
            "icon_name": icon.icon_name,
            "icon_url": icon.icon_url,
            "status": icon.status,
        }
        create_item(db, models.MarkerIcon, icon_data)
        return icon_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_marker_icon(
    db: Session,
    uuid: str,
    model: models.MarkerIcon,
    updated_icon: schemas.MarkerIcon,
):
    try:
        updated_icon_data = {
            "icon_name": updated_icon.icon_name,
            "icon_url": updated_icon.icon_url,
            "status": updated_icon.status,
        }
        update_item(db, uuid, model, updated_icon_data)
        return updated_icon_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_marker_icon(db: Session, uuid: str):
    try:
        return delete_item(db, models.MarkerIcon, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_marker_icon_by_uuid(db: Session, uuid: str):
    try:
        icon = get_item_by_id(db, model=models.MarkerIcon, uuid=uuid)
        return icon
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
