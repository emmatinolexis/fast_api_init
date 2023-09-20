from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from . import models

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

def update_item(db: Session, asset_id: int, updated_item_data):
    db_item = db.query(models.Asset).filter(cast(models.Asset.asset_id, String) == cast(asset_id, String)).first()
    print(db_item)
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

