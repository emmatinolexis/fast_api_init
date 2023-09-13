from fastapi import APIRouter, Depends, HTTPException, status
from app.database import models, schemas

from app.routers.hashing import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
    
)
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated, Union

from app.database import schemas
from sqlalchemy.orm import Session

from .shared import get_db

router = APIRouter(
    prefix="/login",
    tags=["authentication"],
)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/", response_model= None)
async def login_handler(user:schemas.LoginPayload, db: Session = Depends(get_db)) -> any:
    if user.email_address:
           db_user = db.query(models.User).filter(models.User.email_address == user.email_address).first()
           if not db_user:
               raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Invalid Credentials")
           if not verify_password(user.password,db_user.password):
               raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail= "Invalid Credentials")
           access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
           access_token = create_access_token(
            data={"sub": user.email_address}, expires_delta=access_token_expires
            )
           return {"access_token": access_token, "token_type": "bearer", "user": db_user}
    if user.phone_number:
        db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
        if not db_user:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        if not verify_password(user.password,db_user.password):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail= "Invalid Credentials")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.phone_number}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer", "user": db_user}
