from typing import Optional

from pydantic import BaseModel, EmailStr, constr

from app.util.enums import AccountType, UserRole


class UserPayload(BaseModel):
    first_name: str
    last_name: str
    location: Optional[str] = None
    address: Optional[str] = None
    phone_number: constr(max_length=15) = None
    email_address: EmailStr
    password: constr(min_length=6)
    account_type: AccountType
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    role: UserRole

    class Config:
        orm_model = True


class UpdateUserPayload(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone_number: constr(max_length=15) = None

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
