from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .shared import get_db

from app.database import schemas
from app.database.repository import get_all_users, create_user,update_user_by_uuid,get_user_by_email_address
from app.utils.auth import get_current_user, extract_user_data


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/create/", response_model=None)
async def create_user_handler(user: schemas.User, db: Session = Depends(get_db)):
    if get_user_by_email_address(db=db, email=user.email_address):
        raise HTTPException(status_code=400, detail="Email already exists")
    return create_user(db, user)

@router.get("/", response_model=List[schemas.User])
async def get_users_handler(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return get_all_users(db=db)


@router.put("/update/{uuid}", response_model=schemas.UpdateUser)
async def update_user(uuid: str,user: schemas.UpdateUser , db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
     return update_user_by_uuid(uuid = uuid, user = user, db=db)

# @router.delete("/{username}", response_model=None)
# async def delete_user_by_username_handler(username: str, db: Session = Depends(get_db),current_user: schemas.User = Depends(get_current_user)):
#     user = get_user_by_username(db=db, username=username)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_data = extract_user_data(user)
#     db.delete(user)
#     db.commit()
#     return user_data




