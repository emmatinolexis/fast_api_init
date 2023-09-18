from fastapi import APIRouter, Depends
from typing import Annotated

from app.database import models
from fastapi.security import OAuth2PasswordRequestForm
from app.database import schemas
from sqlalchemy.orm import Session

from .shared import get_db
from app.utils.auth import generate_access_token

router = APIRouter(
    prefix="",
    tags=["authentication"],
)

db_user = None

@router.post("/login", response_model= None)
async def login_handler(user: Annotated[OAuth2PasswordRequestForm, Depends()] , db: Session = Depends(get_db)) -> any:
    if user.username:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        access_token = generate_access_token(user,db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

