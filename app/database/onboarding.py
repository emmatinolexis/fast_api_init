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

def get_all_onboardings(db: Session):
    try: 
        onboardings =  get_all_items(db, models.Onboarding)
        return onboardings
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
def create_onboarding(db: Session, onboarding:schemas.Onboarding):
    try:
        onboarding_item = {
            "asset_type_uuid": onboarding.asset_type_uuid,
            "number_of_assets": onboarding.number_of_assets,
            "number_of_months":onboarding.number_of_months,
            "package_uuid":onboarding.package_uuid,
            "user_uuid" : onboarding.user_uuid
        }
        create_item(db, models.Onboarding, onboarding_item)
        return onboarding_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
def update_onboarding(db: Session, onboarding_uuid: str,model: models.Onboarding, onboarding_data: schemas.Onboarding):
    try:
        onboarding_item = {
            "asset_type_uuid": onboarding_data.asset_type_uuid,
            "number_of_assets": onboarding_data.number_of_assets,
            "number_of_months":onboarding_data.number_of_months,
            "package_uuid":onboarding_data.package_uuid,
            "user_uuid" : onboarding_data.user_uuid
        }
        return onboarding_uuid
        update_item(db, onboarding_uuid, model, onboarding_item)
        return onboarding_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
def delete_onboarding(db: Session, uuid: str):
    try:
        return delete_item(db, models.Onboarding, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")

def get_onboarding(db: Session, uuid: str):
    try:
        package = get_item_by_id(db, model=models.Onboarding, uuid=uuid)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")