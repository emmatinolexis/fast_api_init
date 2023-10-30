from typing import Optional,Union

from pydantic import BaseModel,EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
# from app.utils.utils import generate_uuid
# from uuid import UUID, uuid4


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

class GetPackage(BaseModel):
    uuid: str
    
class EmailVerification(BaseModel):
    user_uuid: str
    verification_token: str
    expiry_date: str
    class Config:
        orm_model = True

class UserEmailVerification(BaseModel):
    uuid: str
    class Config:
        orm_model = True

class AssetType(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str
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
    package_item_uuid: str
    package_uuid: str
    class Config:
        orm_model = True

class Feature(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str
    class Config:
        orm_model = True
    
class Equipment(BaseModel):
    equipment_name: str
    equipment_type_uuid: str
    marker_icon_url: str
    marker_icon_colour: str
    class Config:
        orm_model = True
    
class EquipmentType(BaseModel):
    equipment_type_name: str
    class Config:
        orm_model = True

class ContactSale(BaseModel):
    phone: str
    call_time:str
    user_uuid:str
    class Config:
        orm_model = True

class Onboarding(BaseModel):
    asset_type_uuid: str 
    no_of_assets: int
    package_uuid: str
    user_uuid: str
    class Config:
        orm_model = True

class Asset(BaseModel):
    user_uuid: str
    asset_type_uuid: str
    asset_name: str
    equipment_uuid: str
    vin_no: str
    class Config:
        orm_model = True

class Equipment:
    equipment_name:str
    equipment_type_uuid: str
    marker_icon_url: str
    marker_icon_color: str
    class Config:
        orm_model = True

class OnboardingFeatureAssignment:
    onboarding_uuid:str
    feature_uuid: str
    class Config:
        orm_model = True

class EquipmentType:
    equipment_type_name: str
    status: str
    class Config:
        orm_model = True

    


    





   
