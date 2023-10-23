from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.repository import (
    get_all_users,
    create_user,
    get_user_by_username,
    get_user_by_email_address
)
from app.utils.auth import get_current_user
from .shared import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def extract_user_data(user):
    return {
        "username": user.username,
        "phone_number": user.phone_number,
        "email_address": user.email_address
    }

@router.get("/", response_model=List[schemas.User])
async def get_users_handler(db: Session = Depends(get_db)):
    return get_all_users(db=db)

@router.get("/username/{username}", response_model=None)
async def get_user_by_name(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db=db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return extract_user_data(user)

@router.get("/email/{email}", response_model=None)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email_address(db=db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return extract_user_data(user)

@router.post("/", response_model=None)
async def create_user_handler(user: schemas.User, db: Session = Depends(get_db)):
    if get_user_by_email_address(db=db, email=user.email_address):
        raise HTTPException(status_code=400, detail="Email already exists")
    return create_user(db, user)
    


    # if get_user_by_username(db=db, username=user.username):
    #     raise HTTPException(status_code=400, detail="Username already exists")
    # if get_user_by_email(db=db, email=user.email_address):
    #     raise HTTPException(status_code=400, detail="Email address already exists")
    # return create_user(db, user)

@router.put("/{user}")
async def update_username(get_current_user: schemas.User = Depends(get_current_user)):
    pass

@router.delete("/{username}", response_model=None)
async def delete_user_by_username_handler(username: str, db: Session = Depends(get_db),
                                          current_user: schemas.User = Depends(get_current_user)):
    user = get_user_by_username(db=db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = extract_user_data(user)
    db.delete(user)
    db.commit()
    return user_data




