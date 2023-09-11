from sqlalchemy.orm import Session

from . import models, schemas


def get_all_users(db: Session):
    return db.query(models.User).all()


def get_user_by_email_address(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    return (
        db.query(models.User).filter(models.User.phone_number == phone_number).first()
    )


def create_user(db: Session, user: schemas.User):
    db_user = models.User(
        phone_number=user.phone_number,
        email_address=user.email_address,
        password=user.password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_asset_type(db: Session):
    return db.query(models.AssetType).all()


def create_asset_type(db: Session, user_type: schemas.AssetType):
    db_asset = models.AssetType(
        asset_type_name= user_type.asset_type_name,
        status=user_type.status,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset

def update_asset_type(db: Session, asset_type_id: int, updated_asset_type: schemas.AssetType):
    db_asset = db.query(models.AssetType).filter(models.AssetType.id == asset_type_id).first()
    if db_asset:
        db_asset.asset_type_name = updated_asset_type.asset_type_name
        db_asset.status = updated_asset_type.status
        db.commit()
    return db_asset

def delete_asset_type(db: Session, asset_type_id: int):
    db_asset = db.query(models.AssetType).filter(models.AssetType.id == asset_type_id).first()
    if db_asset:
        db.delete(db_asset)
        db.commit()
    return db_asset
