from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.driver import (
    create_driver,
    delete_driver,
    get_all_drivers,
    get_driver_by_uuid,
    update_driver,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"],
)


@router.get("/", response_model=List[schemas.Driver])
async def get_all_drivers_handler(
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_drivers(db)


@router.post("/create", response_model=None)
async def create_driver_handler(
    driver: schemas.Driver,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_driver(db=db, driver=driver)


@router.put("/update/{uuid}", response_model=schemas.Driver)
async def update_driver_handler(
    uuid: str,
    driver: schemas.Driver,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return update_driver(db, uuid, model=models.Driver, updated_driver=driver)


@router.get("/{uuid}", response_model=schemas.Driver)
async def get_driver_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return get_driver_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.Driver)
async def delete_driver_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_driver(db, uuid)
