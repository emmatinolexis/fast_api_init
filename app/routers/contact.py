from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.contact import (
    create_contact,
    delete_contact,
    get_all_contacts,
    get_contact_by_uuid,
    update_contact,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/contact_sales",
    tags=["contact_sales"],
)


@router.get("/", response_model=None)
async def get_all_contacts_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_contacts(db)


@router.post("/create", response_model=None)
async def create_contact_handler(
    contact: schemas.ContactSale,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_contact(db, contact)


@router.put("/update/{uuid}", response_model=None)
async def update_contact_handler(
    uuid: str,
    updated_contact: schemas.ContactSale,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_contact(
        db=db, uuid=uuid, model=models.ContactSale, updated_contact=updated_contact
    )


@router.get("/{uuid}", response_model=None)
async def get_contact_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return get_contact_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=None)
async def delete_contact_by_uuid_handler(uuid: str, db: Session = Depends(get_db),auth_user: schemas.User = Depends(get_current_user)):
    return delete_contact(db, uuid)
