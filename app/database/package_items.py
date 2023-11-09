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


def get_all_package_items(db: Session):
    try:
        package_items = get_all_items(db, models.PackageItem)
        return package_items
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_package_item(db: Session, package_item: schemas.PackageItems):
    try:
        package_item_data = {
            "item_name": package_item.item_name,
            "status": package_item.status,
        }
        created_package_item = create_item(db, models.PackageItem, package_item_data)
        return created_package_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_package_item(
    db: Session,
    package_item_uuid: str,
    model: models.PackageItem,
    updated_package_item: schemas.PackageItems,
):
    try:
        updated_package_item_data = {
            "item_name": updated_package_item.item_name,
            "status": updated_package_item.status,
        }
        updated = update_item(db, package_item_uuid, model, updated_package_item_data)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_package_item(db: Session, uuid: str):
    try:
        return delete_item(db, models.PackageItem, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_package_item_by_uuid(db: Session, uuid: str):
    try:
        package = get_item_by_id(db, model=models.PackageItem, uuid=uuid)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
