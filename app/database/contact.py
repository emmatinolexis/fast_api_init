from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import  HTTPException


from .helpers import (
    get_all_items,
    create_item,
    update_item,
    delete_item,
    get_item_by_id
)


#CRUD functionalities for Assets

def get_all_contacts(db: Session):
    try:
        contacts =  get_all_items(db, models.ContactSale)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    

def create_contact(db: Session, contact: schemas.ContactSale):
    try:
        contact_data = {
            "phone_number": contact.phone_number,
            "call_time": contact.call_time,
            "user_uuid": contact.user_uuid,
        }
        create_item(db, models.ContactSale, contact_data)
        return contact_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    

def update_contact(db: Session, uuid: str, model: models.ContactSale, updated_contact: schemas.ContactSale):
    try:
        updated_contact_data = {
            "phone_number": updated_contact.phone_number,
            "call_time": updated_contact.call_time,
            "user_uuid": updated_contact.user_uuid
        }
        updated = update_item(db,uuid,model,updated_contact_data)
        return updated_contact_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    

def delete_contact(db: Session, uuid: str):
    try:
        return delete_item(db, models.ContactSale, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
def get_contact_by_uuid(db: Session, uuid: str):
    try:
        contact = get_item_by_id(db, model=models.ContactSale, uuid=uuid)
        return contact
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


