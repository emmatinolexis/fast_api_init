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
    contacts =  get_all_items(db, models.ContactSale)
    if contacts:
        return contacts
    raise HTTPException(status_code=404, detail="Contacts Not Found")
    
    

def create_contact(db: Session, contact: schemas.ContactSale, user_uuid: str):
    contact_data = {
        "phone_number": contact.phone_number,
        "call_time": contact.call_time,
        "user_uuid": user_uuid,
    }
    created_contact = create_item(db, models.ContactSale, contact_data)
    if created_contact:
        return created_contact
    raise HTTPException(status_code=500, detail="Error creating contact")
    

def update_contact(db: Session, user_uuid: str,model: models.ContactSale, updated_contact: schemas.ContactSale):
    updated_contact_data = {
        "phone_number": updated_contact.phone_number,
        "call_time": updated_contact.call_time,
        "user_uuid": user_uuid,
    }
    updated = update_item(db, user_uuid,model, updated_contact_data)
    if updated:
        return updated
    raise HTTPException(status_code=500, detail="Error Updating contact")
    

def delete_contact(db: Session, uuid: str):
    return delete_item(db, models.ContactSale, uuid)

def get_contact_by_uuid(db: Session, uuid: str):
    contact = get_item_by_id(db, model=models.ContactSale, uuid=uuid)
    if contact:
        return contact
    raise HTTPException(status_code=404, detail="contact not found")


