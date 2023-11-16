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

# CRUD functionalities for driver


def get_all_drivers(db: Session):
    try:
        driver = get_all_items(db, models.Driver)
        return driver
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_driver(db: Session, driver: schemas.Driver):
    try:
        driver_data = {
            "asset_uuid": driver.asset_uuid,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
            "phone_number": driver.phone_number,
            "license_url": driver.license_url,
        }
        created_driver = create_item(db, models.Driver, driver_data)
        return created_driver
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_driver(
    db: Session,
    driver_uuid: str,
    model: models.Driver,
    updated_driver: schemas.Driver,
):
    try:
        updated_driver_data = {
            "asset_uuid": updated_driver.asset_uuid,
            "first_name": updated_driver.first_name,
            "last_name": updated_driver.last_name,
            "phone_number": updated_driver.phone_number,
            "license_url": updated_driver.license_url,
        }
        updated = update_item(db, driver_uuid, model, updated_driver_data)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_driver(db: Session, uuid: str):
    try:
        return delete_item(db, models.Driver, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_driver_by_uuid(db: Session, uuid: str):
    try:
        driver = get_item_by_id(db, model=models.Driver, uuid=uuid)
        return driver
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
