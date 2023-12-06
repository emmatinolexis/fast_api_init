from uuid import UUID

from pydantic import BaseModel


class Onboarding(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: str
    number_of_months: int
    package_uuid: UUID
    user_uuid: UUID
    features_uuid: list[UUID]

    class Config:
        orm_model = True


class OnboardingInput(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: str
    number_of_months: int
    package_uuid: UUID
    user_uuid: UUID


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


class UserOrganisationAssignment(BaseModel):
    user_uuid: UUID
    business_profile_uuid: UUID

    class Config:
        orm_model = True
