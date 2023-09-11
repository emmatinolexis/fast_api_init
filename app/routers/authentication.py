from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas

from .shared import get_db

from app.database.authentication_repository import (
    login_user_by_email,
    login_user_by_phone
)

router = APIRouter(
    prefix="/login",
    tags=["authentication"],
)


@router.post("/", response_model=schemas.LoginUser)
async def login_handler(user: schemas.LoginUser, db: Session = Depends(get_db)):
    if user.email_address:
        login_user_by_email(db, user)
    
    # if(user.phone_number):
    #     login_user_by_phone(db,user)


