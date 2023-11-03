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

def get_all_packages(db: Session):
    packages =  get_all_items(db, models.Package)
    if packages:
        return packages
    raise HTTPException(status_code=404, detail="Packages Not Found")
    

def create_package(db: Session, package: schemas.Package):
    package_data = {
        "package_name": package.package_name,
        "package_price": package.package_price,
        "package_description": package.package_description,
    }
    created_package = create_item(db, models.Package, package_data)
    if create_package:
        return created_package
    raise HTTPException(status_code=500, detail="Error creating package")
    

def update_package(db: Session, package_uuid: str,model: models.Package, updated_package: schemas.Package):
    updated_package_data = {
        "package_name": updated_package.package_name,
        "package_price": updated_package.package_price,
        "package_description": updated_package.package_description,
    }
    updated = update_item(db, package_uuid,model, updated_package_data)
    if updated:
        return updated
    raise HTTPException(status_code=500, detail="Error Updating package")
    

def delete_package(db: Session, uuid: str):
    return delete_item(db, models.Package, uuid)

def get_package_by_uuid(db: Session, uuid: str):
    package = get_item_by_id(db, model=models.Package, uuid=uuid)
    if package:
        return package
    raise HTTPException(status_code=404, detail="Package not found")


def assign_package_item(db: Session, data: schemas.PackageItemAssignment):
    # return data.package_item_uuids
    try:
        for item in data.package_item_uuids:

            data_items = {
                "package_uuid" : data.package_uuid,
                "package_item_uuid" : item
            }

            db_item = db.query(models.PackageItemAssignment).filter(
            models.PackageItemAssignment.package_uuid == data.package_uuid,
            models.PackageItemAssignment.package_item_uuid == item
            ).first()

            if db_item:
                pass
            else:
                create_item(db, models.PackageItemAssignment, data_items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
    raise HTTPException(status_code=200, detail="Success")

def delete_package_item(db: Session, package_uuid: str, package_item_uuid: str):
    try:
        db_item = db.query(models.PackageItemAssignment).filter(
                models.PackageItemAssignment.package_uuid == package_uuid,
                models.PackageItemAssignment.package_item_uuid == package_item_uuid
                ).first()
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
        
    