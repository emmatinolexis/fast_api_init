from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.repository import (
    create_user,
    get_all_users,
    get_user_by_email_address,
    update_user_by_uuid,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/create", response_model=None)
async def create_user_handler(user: schemas.User, db: Session = Depends(get_db)):
    get_user = get_user_by_email_address(user.email_address, db)
    if get_user:
        raise HTTPException(status_code=400, detail="User Already exist")
    else:
        return create_user(db, user)


@router.get("/", response_model=List[schemas.User])
async def get_users_handler(
    db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)
):
    return get_all_users(db=db)


@router.put("/update/{uuid}", response_model=schemas.UpdateUser)
async def update_user(
    uuid: str,
    user: schemas.UpdateUser,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_user_by_uuid(uuid=uuid, user=user, db=db)


@router.get("/{email_address}", response_model=None)
async def get_user_by_email(email_address, db: Session = Depends(get_db)):
    result = get_user_by_email_address(email_address, db=db)
    if result:
        raise HTTPException(status_code=200, detail="User found")
    raise HTTPException(status_code=201, detail="User Not Found")
