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

# CRUD functionalities for organization contact


def get_all_contacts(db: Session):
    try:
        contacts = get_all_items(db, models.OrganisationContact)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_contact(db: Session, contact: schemas.OrganisationContact):
    try:
        contact_data = {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "role": contact.role,
            "country": contact.country,
            "message": contact.message,
            "user_uuid": contact.user_uuid,
        }
        # return contact_data
        create_item(db, models.OrganisationContact, contact_data)
        return contact_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_contact(
    db: Session,
    contact_uuid: str,
    model: models.OrganisationContact,
    updated_contact: schemas.OrganisationContact,
):
    try:
        updated_data = {
            "first_name": updated_contact.first_name,
            "last_name": updated_contact.last_name,
            "role": updated_contact.role,
            "country": updated_contact.country,
            "message": updated_contact.message,
            "user_uuid": updated_contact.user_uuid,
        }
        update_item(db, contact_uuid, model, updated_data)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_contact(db: Session, uuid: str):
    try:
        return delete_item(db, models.OrganisationContact, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_contact_by_uuid(db: Session, uuid: str):
    try:
        feature = get_item_by_id(db, model=models.OrganisationContact, uuid=uuid)
        return feature
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
