from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from .shared import get_db

from app.database import models, schemas
from app.utils.auth import generate_access_token
from app.utils.auth import verify_token
from app.utils.email import read_email_template
from app.utils.hashing import verify_token

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


router = APIRouter(
    prefix="",
    tags=["authentication"],
)

db_user = None

port = 587
smtp_server = "live.smtp.mailtrap.io"
login = "1de0bb762bb183"
password = "ae4bfeca11542d"



@router.post("/verify-token")
async def verify_token_route(token_data: schemas.VerifyToken):
    if verify_token(token_data.Token):
        return {"message": "Token is valid"}
    else:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")



@router.post("/verify-email")
async def verify_user_email(email:schemas.EmailVerification):
    sender_email = "tariqsulley3c@gmail.com"
    receiver_email = "tariqsulley3c@gmail.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = "MVI Tracking Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email
    html_content = read_email_template() 

    html_payload = MIMEText(html_content, "html")
    message.attach(html_payload)

    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
        server.login(login, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    return {"done":"success"}


# async def login_handler(user: Annotated[OAuth2PasswordRequestForm, Depends()] , db: Session = Depends(get_db)):
@router.post("/login", response_model=None)
async def login_handler(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email_address == user.email_address).first()
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    user_dict = {
    "username": db_user.username,
    "phone_number": db_user.phone_number,
    "email_address": db_user.email_address,
    "verifiedAt":db_user.verifiedAt
    }
    access_token = generate_access_token(user,db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_dict}
