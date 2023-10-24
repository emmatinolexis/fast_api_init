from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from .shared import get_db

from app.database import models
from app.database import schemas
from app.routers.users import extract_user_data
from app.utils.auth import generate_access_token
from app.utils.auth import verify_token_frontend
from app.utils.email import read_email_template
from app.utils.hashing import verify_token
from app.utils.email import send_email
from app.utils.auth import generate_verification_token


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



# This endpoint serves a crucial security function for users who choose to register via email.
# Upon successful registration, the user's access token is stored within a cookie.
# To ensure the legitimacy of the token and prevent unauthorized generation of tokens,
# the token within the cookie undergoes a verification process.

@router.post("/verify-token")
async def verify_token_route(token_data: schemas.VerifyToken):
    # send_email("Test Email","nuellexis@gmail.com", 'This is my message to you')
    if verify_token_frontend(token_data.Token):
        return {"message": "Token is valid"}
    else:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


@router.post("/verify-email")
async def verify_user_email():
    # generate verify_token
    # update user details with generated token in verificatin_token
    #send veriy email to user 
    verify_token = generate_verification_token()
    return verify_token
    # sender_email = "tariqsulley3c@gmail.co"
    # receiver_email = "tariqsulley3c@gmail.com"
    # message = MIMEMultipart("alternative")
    # message["Subject"] = "MVI Tracking Email Verification"
    # message["From"] = sender_email
    # message["To"] = receiver_email
    # html_content = read_email_template().replace("{name}","Ganda")

    # html_payload = MIMEText(html_content, "html")
    # message.attach(html_payload)

    # with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
    #     server.login(login, password)
    #     server.sendmail(
    #         sender_email, receiver_email, message.as_string()
    #     )
    # return {"done":"success"}


# async def login_handler(user: Annotated[OAuth2PasswordRequestForm, Depends()] , db: Session = Depends(get_db)):

@router.post("/login", response_model=None)
async def login_handler(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email_address == user.email_address).first()

    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    user_dict = extract_user_data(db_user)
    access_token = generate_access_token(user,db_user)
    return {"access_token": access_token, "user": user_dict, "permission":""}
