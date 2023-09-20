from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.repository import get_all_users
from app.database.repository import create_user
from app.database.repository import get_user_by_username
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
    user_by_name = get_user_by_username(db=db, username=user.username)
    if user_by_name:
        raise HTTPException(status_code=400, detail="Username already exists")
    return create_user(db, user)
