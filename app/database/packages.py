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
    try:
        db_packages =  get_all_items(db, models.Package)
        packages = []
        for package in db_packages:
            package_items = db.query(models.PackageItem).join(models.PackageItemAssignment, models.PackageItemAssignment.package_item_uuid == models.PackageItem.uuid).filter(models.PackageItemAssignment.package_uuid == package.uuid).all()
            # package_item = db_item = db.query(models.PackageItem).filter(
            # # models.PackageItem.uuid == package.,
            # ).first()

            packages.append({
                "package": package,
                # "package_items": package.package_item_assignments if package.package_item_assignments else None
                "package_items": package_items

            })
        return packages
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    

def create_package(db: Session, package: schemas.Package):
    try:
        package_data = {
            "package_name": package.package_name,
            "package_price": package.package_price,
            "package_description": package.package_description,
        }
        created_package = create_item(db, models.Package, package_data)
        return created_package

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
    

def update_package(db: Session, package_uuid: str,model: models.Package, updated_package: schemas.Package):
    try:
        updated_package_data = {
            "package_name": updated_package.package_name,
            "package_price": updated_package.package_price,
            "package_description": updated_package.package_description,
        }
        updated = update_item(db, package_uuid,model, updated_package_data)
        return updated

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    

def delete_package(db: Session, uuid: str):
    try:
        return delete_item(db, models.Package, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")

def get_package_by_uuid(db: Session, uuid: str):
    try:
        package = get_item_by_id(db, model=models.Package, uuid=uuid)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
        


def assign_package_item(db: Session, data: schemas.PackageItemAssignment):
    # return data.package_item_uuids
    try:
        for item in data.package_item_uuids:

            data_items = {
                "package_uuid" : data.package_uuid,
                "package_item_uuid" : item
            }

            db_item = db.query(models.PackageItemAssignment).filter(
            models.PackageItemAssignment.package_item_uuid == item,
            models.PackageItemAssignment.package_uuid == data.package_uuid
            ).first()

            if db_item:
                pass
            else:
                create_item(db, models.PackageItemAssignment, data_items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return HTTPException(status_code=200, detail="success")

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
        
    