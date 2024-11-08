from typing import Optional, List
from uuid import UUID

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, constr, field_validator

from app.util.enums import AccountType, ActiveStatus, DriverType, UserRole


class UserPayload(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    password: constr(min_length=6)
    account_type: AccountType
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    business_profile_uuid: Optional[UUID] = None
    role: Optional[UserRole] = UserRole.CUSTOMER
    user_role_uuid: Optional[UUID] = None
    invite_status: Optional[bool] = None
    status: ActiveStatus = ActiveStatus.ACTIVE

    class Config:
        orm_model = True


class DriverLicenseUpdates(BaseModel):
    license_number: str
    front_url: str
    back_url: str
    expiration_date: str


class DriversLicenseFull(BaseModel):
    license_number: str
    front_url: str
    back_url: str
    expiration_date: str
    user_id: str


class UpdateInstallerLocation(BaseModel):
    installer_locations: List[str]


class UpdateUserPayload(BaseModel):
    location: str
    address: str
    phone_number: str
    country: str
    operator_type: Optional[DriverType] = None
    license: Optional[DriverLicenseUpdates] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str, info: ValidationInfo) -> str:
        try:
            phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError("Invalid phone number format")

            if not phonenumbers.is_possible_number(phone_number):
                raise ValueError("Invalid phone number")
            return value
        except phonenumbers.NumberParseException as e:
            raise ValueError(f"Invalid phone number: {e}")

    class Config:
        orm_model = True


class UserProfileUdatePayload(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None


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


class AccountDeactivationPayload(BaseModel):
    reason: str


class UpdateUserAvatar(BaseModel):
    avatar_url: str = Field(min_length=3, max_length=200)


class UpdatePhoneNumber(BaseModel):
    phone_number: str = Field(min_length=10, max_length=20)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str, info: ValidationInfo) -> str:
        try:
            phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError("Invalid phone number format")

            if not phonenumbers.is_possible_number(phone_number):
                raise ValueError("Invalid phone number")
            return value
        except phonenumbers.NumberParseException as e:
            raise ValueError(f"Invalid phone number: {e}")


class UserPhoneVerificationToken(BaseModel):
    token: str = Field(min_length=6, max_length=6)


class UpdateAdminTeamMemberPayload(BaseModel):
    status: Optional[ActiveStatus] = None
    user_role_uuid: Optional[UUID] = None

    class Config:
        orm_model = True


class InstallerResponse(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    installer_locations: Optional[List[str]] = None

    class Config:
        orm_mode = True
        from_attributes = True
