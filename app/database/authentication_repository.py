from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated, Union


from app.routers.hashing import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
    
)

from fastapi import HTTPException, status

from . import models, schemas




def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user_by_email(db: Session, user: schemas.LoginUser):
        # get user from DB
        db_user = db.query(models.User).filter(models.User.email_address == user.email_address).first()
        
        # check if user exist if not throw erro
        if not db_user:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        
        # check user password
        if not verify_password(user.password,db_user.password):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        # Generate User access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email_address}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user": db_user}
        
        
        
def login_user_by_phone(db: Session, user: schemas.LoginUser):
        # get user from DB
        db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
        # check if user exist if not throw erro
        if not db_user:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        # check user password
        if not verify_password(user.password,db_user.password):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        
        # Generate User access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email_address}, expires_delta=access_token_expires
        )
        
        # pass user and access token in response
        return {"access_token": access_token, "token_type": "bearer", "user": db_user}

