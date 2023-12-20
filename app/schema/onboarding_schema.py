from uuid import UUID

from pydantic import BaseModel

from app.util.enums import AccountType


class OnboardingPayload(BaseModel):
    number_of_assets: int
    number_of_months: int
    package_uuid: UUID
    user_uuid: UUID
    features_uuid: list[UUID]

    class Config:
        orm_model = True


class OnboardingUpdatePayload(BaseModel):
    number_of_assets: int
    number_of_months: int

    class Config:
        orm_model = True


class OnboardingIndividualInput(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: int
    number_of_months: int
    package_uuid: UUID
    user_uuid: UUID
    onboarding_type: AccountType


class OnboardingBusinessInput(BaseModel):
    number_of_assets: int
    user_uuid: UUID
    onboarding_type: AccountType


class BusinessOnboardingPayload(BaseModel):
    asset_types_uuid: list[UUID]
    number_of_assets: int
    user_uuid: UUID
    features_uuid: list[UUID]

    class Config:
        orm_model = True


class OnboardingFeatureAssignment(BaseModel):
    onboarding_uuid: UUID
    feature_uuid: UUID

    class Config:
        orm_model = True


class OnboardingAssetTypeAssignment(BaseModel):
    onboarding_uuid: UUID
    asset_type_uuid: UUID

    class Config:
        orm_model = True


class OrganisationContactPayload(BaseModel):
    first_name: str
    last_name: str
    role: str
    country: str
    message: str
    user_uuid: UUID

    class Config:
        orm_model = True


class BusinessProfile(BaseModel):
    business_name: str
    business_email: str
    business_phone: str
    business_logo: str = None
    business_address: str = None
    business_location: str = None


class UserOrganisationAssignment(BaseModel):
    user_uuid: UUID
    business_profile_uuid: UUID

    class Config:
        orm_model = True
