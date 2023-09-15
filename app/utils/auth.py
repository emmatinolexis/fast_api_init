from fastapi import APIRouter, Depends, HTTPException, status
from app.database import schemas
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException, status
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


from app.utils.hashing import (
    verify_password,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)

from datetime import datetime, timedelta
from jose import jwt
from typing import Union

from app.database import schemas
from sqlalchemy.orm import Session

from app.routers.shared import get_db

router = APIRouter(
    prefix="/login",
    tags=["authentication"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_access_token(user:schemas.LoginPayload, db_user, db: Session = Depends(get_db)):
    if not db_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Invalid Credentials")
    if not verify_password(user.password,db_user.password):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail= "Invalid Credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email_address}, expires_delta=access_token_expires)
    return access_token

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return  verify_token(token, credentials_exception);
 
    
