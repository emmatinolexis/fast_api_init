from fastapi import APIRouter, Depends
from app.database import models, schemas

from app.database import models
from fastapi.security import OAuth2PasswordRequestForm
from app.database import schemas
from sqlalchemy.orm import Session
import datetime
from app.utils.hashing import SECRET_KEY
from app.utils.hashing import ALGORITHM
from .shared import get_db
from app.utils.auth import generate_access_token
from jose import jwt
router = APIRouter(
    prefix="",
    tags=["authentication"],
)

db_user = None
sessions  = {}


@router.post("/", response_model= None)
async def login_handler(user:schemas.LoginPayload, db: Session = Depends(get_db)) -> any:
    if user.email_address:
        db_user = db.query(models.User).filter(models.User.email_address == user.email_address).first()
        access_token = generate_access_token(user,db_user)
    
    if user.phone_number:
        db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
        access_token = generate_access_token(user,db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

@router.get("/logout")
async def logout_handler(db: Session = Depends(get_db)):
    pass

