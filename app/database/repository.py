from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.helpers import get_all_items
from app.utils.hashing import hash_user_password
from app.utils.auth import extract_user_data
from app.utils.email import send_email
from datetime import datetime, timedelta
from app.utils.hashing import VERIFY_TOKEN_EXPIRE_DAYS



from . import models, schemas
from .helpers import get_all_items
import uuid

def get_all_users(db: Session):
    return get_all_items(db, models.User)

def update_user_by_uuid(db:Session,uuid:str, user : schemas.User):
    user_to_update = db.query(models.User).filter(models.User.uuid == uuid).first()
    user_to_update.phone_number = user.phone_number
    user_to_update.address = user.address
    user_to_update.location = user.location

    db.commit()
    db.refresh(user_to_update)
    return user

def get_user_by_email_address(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
def hash_user_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
    return pwd_context.hash(password)

def create_user(db: Session, user: schemas.User):
    db_user = models.User(
        first_name = user.first_name,
        last_name = user.last_name,
        location = user.location,
        address = user.address,
        phone_number=user.phone_number,
        email_address=user.email_address,
        password=hash_user_password(user.password),
    )

    db.add(db_user)
    db.commit()
    # db.refresh(db_user)

    # created_user = db.query(models.User).filter(models.User.email_address == db_user.email_address).first()
    
    returned_user = {
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "location": db_user.location,
        "address": db_user.address,
        "phone_number": db_user.phone_number,
        "email_address": db_user.email_address,
        "uuid": db_user.uuid
    } 

    return returned_user

def create_verification_token(db: Session, user_verify: schemas.UserEmailVerification, verification_token:schemas.EmailVerification) -> bool:
    
    current_date = datetime.now()
    # return user_verify
    
    db_verify = models.EmailVerification(
        user_uuid = user_verify.uuid,
        verification_token = verification_token["verification_token"],
        expiry_date = current_date + timedelta(days=VERIFY_TOKEN_EXPIRE_DAYS)
    )

    db.add(db_verify)
    db.commit()

    db_user = db.query(models.User).filter(models.User.uuid == user_verify.uuid).first() 

    # return result
    #send email
    subject="MVI tracking email verification"
    
    message = "Please use the button link below to verify your account and get started with MVI tracking solutions."

    return send_email(subject=subject,recipient=db_user.first_name,email=db_user.email_address, message=message, token=db_verify.verification_token)


