from typing import List, Optional, Union

# from app.utils.utils import generate_uuid
from uuid import UUID

from pydantic import BaseModel, EmailStr

# from app.utils.enums import ActiveInactive

# from pydantic_extra_types.phone_numbers import PhoneNumber

# class BaseUUIDModel(BaseModel):
#     uuid: UUID = Field(default_factory=uuid4)


class User(BaseModel):
    first_name: str
    last_name: str
    location: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]
    email_address: EmailStr
    password: str

    class Config:
        orm_model = True


class UpdateUser(BaseModel):
    location: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]

    class Config:
        orm_model = True


class UserLogin(BaseModel):
    email_address: EmailStr
    password: str

    class Config:
        orm_model = True


class UserEmail(BaseModel):
    email_address: str

    class Config:
        orm_model = True


class GetPackage(BaseModel):
    uuid: str


class EmailVerification(BaseModel):
    user_uuid: UUID
    verification_token: str
    expiry_date: str

    class Config:
        orm_model = True


class UserEmailVerification(BaseModel):
    uuid: str

    class Config:
        orm_model = True


class AssetTypeInput(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str

    class Config:
        orm_model = True


class AssetType(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True


class VerifyToken(BaseModel):
    Token: str

    class Config:
        orm_model = True


class TokenData(BaseModel):
    username: Union[str, None] = None


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_model = True


class PackageItems(BaseModel):
    item_name: str
    status: str

    class Config:
        orm_model = True


class Package(BaseModel):
    package_name: str
    package_price: str
    package_description: str

    class Config:
        orm_model = True


class PackageItemAssignment(BaseModel):
    package_item_uuids: List[UUID]
    package_uuid: UUID

    class Config:
        orm_model = True


class PackageOutput(BaseModel):
    package_name: str
    package_price: str
    package_description: str
    uuid: UUID
    # package_item:PackageItemAssignment

    class Config:
        orm_model = True


class FeatureInput(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str

    class Config:
        orm_model = True


class Feature(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True


# class Equipment(BaseModel):
#     equipment_name: str
#     equipment_type_uuid: UUID
#     marker_icon_url: str
#     marker_icon_colour: str

#     class Config:
#         orm_model = True


class ContactSale(BaseModel):
    phone_number: str
    call_time: str
    user_uuid: UUID
    status: str

    class Config:
        orm_model = True


class Onboarding(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: str
    number_of_months: int
    package_uuid: UUID
    user_uuid: UUID
    features_uuid: list[UUID]

    class Config:
        orm_model = True


class BusinessOnboarding(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: str
    user_uuid: UUID
    features_uuid: list[UUID]
    business_name: str
    business_email: str
    business_location: str
    business_phone: str
    business_logo: str
    business_address: str

    class Config:
        orm_model = True


class MarkerIcon(BaseModel):
    icon_name: str
    icon_url: str
    status: str

    class Config:
        orm_model = True


class Equipment(BaseModel):
    name: str
    status: str


class EquipmentType(BaseModel):
    equipment_type_name: str
    uuid: UUID
    status: str
    equipment_uuid: Optional[UUID] = None

    class Config:
        orm_model = True


class EquipmentTypeCreate(BaseModel):
    equipment_type_name: str
    status: str
    equipment_uuid: Optional[UUID] = None

    class Config:
        orm_model = True


class Asset(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: str
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_no: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None

    class Config:
        orm_model = True


class AssetCreate(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: str
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_no: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None

    class Config:
        orm_model = True


class OnboardingFeatureAssignment(BaseModel):
    onboarding_uuid: UUID
    feature_uuid: UUID

    class Config:
        orm_model = True


class OrganisationContact(BaseModel):
    first_name: str
    last_name: str
    role: str
    country: str
    message: str
    user_uuid: UUID

    class Config:
        orm_model = True


class BusinessProfile(BaseModel):
    businness_name: str
    business_email: str
    business_phone: str
    user_uuid: UUID


class AssetLocation(BaseModel):
    asset_uuid: UUID
    longitude: str
    latitude: str


class AssetLocationFetch(BaseModel):
    asset_uuid: UUID
    longitude: str
    latitude: str
    created_at: str


class Driver(BaseModel):
    asset_uuid: UUID
    first_name: str
    last_name: str
    phone_number: str
    license_url: str
    profile_picture_url: str


class AlertPolicyType(BaseModel):
    name: str
    description: str
    status: str
