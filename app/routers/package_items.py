from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database import schemas, models
from sqlalchemy.orm import Session
from app.utils.auth import get_current_user
from .shared import get_db

from app.database.package_items import (
    get_all_package_items,
    create_package_item,
    update_package_item,
    get_package_item_by_uuid,
    delete_package_item,
)

router = APIRouter(
    prefix="/package_items",
    tags=["package_items"],
)

@router.get("/", response_model=List[schemas.PackageItems])
async def get_product_packages_items_handler(db: Session = Depends(get_db),  auth_user: schemas.User = Depends(get_current_user)):
    return get_all_package_items(db)

@router.post("/create", response_model=None)
async def create_package_item_handler(package_item:schemas.PackageItems, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return create_package_item(db=db,package_item = package_item)

@router.put("/update/{uuid}", response_model=schemas.PackageItems)
async def update_package_item_handler(uuid:str, package_item:schemas.PackageItems, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return update_package_item(db,uuid,model=models.PackageItem,updated_package_item=package_item)

@router.get("/{uuid}", response_model=schemas.PackageItems)
async def get_package_item_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return get_package_item_by_uuid(db,uuid)

@router.delete("/delete/{uuid}", response_model=schemas.PackageItems)
async def delete_package_item_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return delete_package_item(db,uuid)