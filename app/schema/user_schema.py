from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr

from app.util.enums import AccountType, UserRole


class UserPayload(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    password: constr(min_length=6)
    account_type: AccountType
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    role: Optional[UserRole] = UserRole.CUSTOMER

    class Config:
        orm_model = True


class UpdateUserPayload(BaseModel):
    location: str
    address: str
    phone_number: constr(max_length=15)

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


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    password_confirmation: str

    class Config:
        orm_model = True


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str
    password_confirmation: str

    class Config:
        orm_model = True


class IndividualUser(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    uuid: UUID
    account_type: AccountType
    role: UserRole


class BussinessUser(IndividualUser):
    business_name: str
    business_email: str
    business_phone: str
