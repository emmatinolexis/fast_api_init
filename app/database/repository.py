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


def create_asset_type(db: Session, user_type: schemas.AssetType):
    db_asset = models.AssetType(
        asset_type_name= user_type.asset_type_name,
        status=user_type.status,
    )

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset
