from typing import Optional

from pydantic import BaseModel, EmailStr

from app.util.enums import AccountType


class UserPayload(BaseModel):
    first_name: str
    last_name: str
    location: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: EmailStr
    password: str
    account_type: AccountType
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None

    class Config:
        orm_model = True


class FindUserResult(BaseModel):
    first_name: str
    last_name: str
    location: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: EmailStr
    account_type: AccountType
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None

    class Config:
        orm_model = True


class UpdateUserPayload(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        orm_model = True


class UserLogin(BaseModel):
    email_address: EmailStr
    password: str

    class Config:
        orm_model = True


class UserEmail(BaseModel):
    email_address: EmailStr

    class Config:
        orm_model = True
