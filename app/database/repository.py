from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.utils.hashing import (
    hash_user_password,  
)


from . import models, schemas

def get_all_users(db: Session):
    return db.query(models.User).all()


def get_user_by_username(db:Session,username:str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email_address(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    return (
        db.query(models.User).filter(models.User.phone_number == phone_number).first()
    )
    
def create_user(db: Session, user: schemas.User):
    db_user = models.User(
        username = user.username,
        phone_number=user.phone_number,
        email_address=user.email_address,
        password=hash_user_password(user.password),
    ) 

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
