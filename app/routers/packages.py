from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database import schemas, models
from sqlalchemy.orm import Session
from app.utils.auth import get_current_user
from .shared import get_db

from app.database.packages import (
    get_all_packages,
    create_package,
    update_package,
    get_package_by_uuid,
    delete_package,
    assign_package_item,
    delete_package_item
)
 

router = APIRouter(
    prefix="/packages",
    tags=["packages"],
)

@router.get("/", response_model=None)
async def get_product_packages_handler(db: Session = Depends(get_db),  auth_user: schemas.User = Depends(get_current_user)):
    return get_all_packages(db)
    
@router.post("/create", response_model=None)
async def create_package_handler(package:schemas.Package, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return create_package(db=db,package = package)

@router.put("/update/{uuid}", response_model=schemas.Package)
async def update_package_handler(uuid:str, package:schemas.Package, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return update_package(db,uuid,model=models.Package,updated_package=package)

@router.get("/{uuid}", response_model=schemas.Package)
async def get_package_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return get_package_by_uuid(db,uuid)

@router.delete("/delete/{uuid}", response_model=schemas.Package)
async def delete_package_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return delete_package(db,uuid)

@router.post("/package_item_assignment", response_model=None)
async def assign_package_item_handler(data: schemas.PackageItemAssignment, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return assign_package_item(db,data)

@router.delete("/package_item_assignment/{package_uuid}/{package_item_uuid}", response_model=None)
async def delete_package_item_from_package_handler(package_uuid, package_item_uuid, db: Session = Depends(get_db),auth_user: schemas.User = Depends(get_current_user)):
    return delete_package_item(db,package_uuid,package_item_uuid)

 
