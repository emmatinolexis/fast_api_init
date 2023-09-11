from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

def get_all_items(db: Session, model):
    return db.query(model).all()

def get_item_by_id(db: Session, model, item_id: int):
    return db.query(model).filter(model.id == item_id).first()

def create_item(db: Session, model, item_data):
    db_item = model(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, model, item_id: int, updated_item_data):
    db_item = get_item_by_id(db, model, item_id)
    if db_item:
        for key, value in updated_item_data.items():
            setattr(db_item, key, value)
        db.commit()
    return db_item

def delete_item(db: Session, model, item_id: int):
    db_item = get_item_by_id(db, model, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def get_all_users(db: Session):
    return get_all_items(db, models.User)

def get_user_by_email_address(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.User):
    user_data = {
        "phone_number": user.phone_number,
        "email_address": user.email_address,
        "password": user.password,
    }
    return create_item(db, models.User, user_data)
    
    
def hash_user_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
    return pwd_context.hash(password)


def get_all_assets(db: Session):
    return get_all_items(db, models.Asset)

def create_asset(db: Session, asset: schemas.Asset):
    asset_data = {
        "asset_name": asset.asset_name,
        "asset_type_id": asset.asset_type_id,
        "status": asset.status,
        "customer_id": asset.customer_id
    }
    return create_item(db, models.Asset, asset_data)

def update_asset(db: Session, asset_id: int, updated_asset: schemas.Asset):
    updated_asset_data = {
        "asset_name": updated_asset.asset_name,
        "asset_type_id": updated_asset.asset_type_id,
        "status": updated_asset.status,
        "customer_id": updated_asset.customer_id
    }
    return update_item(db, models.Asset, asset_id, updated_asset_data)

def delete_asset(db: Session, asset_id: int):
    return delete_item(db, models.Asset, asset_id)


def get_asset_type(db: Session):
    return get_all_items(db, models.AssetType)

def create_asset_type(db: Session, asset_type: schemas.AssetType):
    asset_type_data = {
        "asset_type_name": asset_type.asset_type_name,
        "status": asset_type.status,
    }
    return create_item(db, models.AssetType, asset_type_data)

def update_asset_type(db: Session, asset_type_id: int, updated_asset_type: schemas.AssetType):
    updated_asset_type_data = {
        "asset_type_name": updated_asset_type.asset_type_name,
        "status": updated_asset_type.status,
    }
    return update_item(db, models.AssetType, asset_type_id, updated_asset_type_data)

def delete_asset_type(db: Session, asset_type_id: int):
    return delete_item(db, models.AssetType, asset_type_id)
