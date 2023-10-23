from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.helpers import get_all_items
from app.utils.hashing import hash_user_password

from . import models, schemas
from .helpers import get_all_items


def get_all_users(db: Session):
    return get_all_items(db, models.User)

def get_user_by_username(db:Session,username:str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email_address(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
def hash_user_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
    return pwd_context.hash(password)

def create_user(db: Session, user: schemas.User):
    db_user = models.User(
        # username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        location = user.location,
        address = user.address,
        phone_number=user.phone_number,
        email_address=user.email_address,
        password=hash_user_password(user.password),
        verifiedAt  = user.verifiedAt
    ) 
    user_dict = {
        "first_name" : user.first_name,
        "last_name" : user.last_name,
        "location" : user.location,
        "address" : user.address,
        "phone_number": user.phone_number,
        "email_address": user.email_address,
        "verifiedAt": user.verifiedAt
    }
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user_dict
