from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database import schemas, models
from sqlalchemy.orm import Session
from app.utils.auth import get_current_user
from .shared import get_db

from app.database.contact import (
    get_all_contacts,
    create_contact,
    update_contact,
    get_contact_by_uuid,
    delete_contact,

)
 
router = APIRouter(
    prefix="/contact_sales",
    tags=["contact_sales"],
)

@router.get("", response_model=List[schemas.ContactSale])
async def get_all_contacts_handler(db: Session = Depends(get_db),  auth_user: schemas.User = Depends(get_current_user)):
    return get_all_contacts(db)
    
@router.post("/create", response_model=None)
async def create_contact_handler(user_uuid:str,contact:schemas.ContactSale, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return create_contact(db=db,contact = contact,user_uuid=user_uuid)

# @router.put("/update/{uuid}", response_model=schemas.ContactSale)
# async def update_contact_handler(uuid:str,contact:schemas.ContactSale, db: Session = Depends(get_db)):
#     return update_contact(db,uuid,model=models.ContactSale,updated_contact=contact)
@router.put("/update/{uuid}", response_model=schemas.ContactSale)
async def update_contact_handler(uuid: str, contact: schemas.ContactSale, db: Session = Depends(get_db)):
    return update_contact(db=db, user_uuid=uuid, model=models.ContactSale, updated_contact=contact)

@router.get("/{uuid}", response_model=schemas.ContactSale)
async def get_contact_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return get_contact_by_uuid(db,uuid)

@router.delete("/delete/{uuid}", response_model=schemas.ContactSale)
async def delete_contact_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return delete_contact(db,uuid)