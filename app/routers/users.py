from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import schemas
from app.database.repository import (
    get_all_users,
    get_user_by_email_address,
    get_user_by_phone_number,
    create_user,
)
from .shared import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/", response_model=List[schemas.User])
async def get_users_handler(db: Session = Depends(get_db)):
    return get_all_users(db=db)


@router.post("/", response_model=schemas.User)
async def create_user_handler(user: schemas.User, db: Session = Depends(get_db)):
    user_by_email = get_user_by_email_address(db=db, email=user.email_address) 
    if user_by_email:
        raise HTTPException(status_code=400, detail="User with email already exists.")

    user_by_phone = get_user_by_phone_number(db=db, phone_number=user.phone_number)
    if user_by_phone:
        raise HTTPException(
            status_code=400, detail="User with phone number already exists."
        )

    return create_user(db, user)
