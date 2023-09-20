from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.database import models
from app.utils.auth import generate_access_token
from sqlalchemy.orm import Session
from .shared import get_db

router = APIRouter(
    prefix="",
    tags=["authentication"],
)

db_user = None

@router.post("/login", response_model= None)
async def login_handler(user: Annotated[OAuth2PasswordRequestForm, Depends()] , db: Session = Depends(get_db)):
    if user.username:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        user_dict = {
        "username": db_user.username,
        "phone_number": db_user.phone_number,
        "email_address": db_user.email_address
        }
        access_token = generate_access_token(user,db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_dict}

