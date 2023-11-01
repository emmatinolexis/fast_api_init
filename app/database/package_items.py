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

def get_all_package_items(db: Session):
    package_items =  get_all_items(db, models.PackageItem)
    if package_items:
        return package_items
    raise HTTPException(status_code=404, detail="Package items not found")
    
    

def create_package_item(db: Session, package_item: schemas.PackageItems):
    package_item_data = {
        "item_name": package_item.item_name,
        "status": package_item.status,
    }
    created_package_item = create_item(db, models.PackageItem, package_item_data)
    if created_package_item:
        return created_package_item
    raise HTTPException(status_code=500, detail="Error creating package")
    

def update_package_item(db: Session, package_item_uuid: str,model: models.PackageItem, updated_package_item: schemas.PackageItems):
    updated_package_item_data = {
        "item_name": updated_package_item.item_name,
        "status": updated_package_item.status
    }
    updated = update_item(db, package_item_uuid,model, updated_package_item_data)
    if updated:
        return updated
    raise HTTPException(status_code=500, detail="Error Updating package item")
    

def delete_package_item(db: Session, uuid: str):
    return delete_item(db, models.PackageItem, uuid)

def get_package_item_by_uuid(db: Session, uuid: str):
    package = get_item_by_id(db, model=models.PackageItem, uuid=uuid)
    if package:
        return package
    raise HTTPException(status_code=404, detail="Package item not found")

