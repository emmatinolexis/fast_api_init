from typing import Optional
from typing import  Union

from pydantic import BaseModel
from pydantic import EmailStr
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
    
class UserLogin(BaseModel):
    email_address: EmailStr
    password: str
    
class EmailVerification(BaseModel):
    user_id: str
    verification_token: str
    expiry_date: str

class UserEmailVerification(BaseModel):
    user_id: int

class AssetType(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str
    class Config:
        orm_model = True

class Asset(BaseModel):
    asset_name: str
    asset_id: int
    asset_status: str
    user_id: int
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
 
class PackageItems(BaseModel):
    item_name: str
    status: str
    
class Package(BaseModel):
    package_name: str
    package_price: str
    package_description: str
    
class PackageItemAssignment(BaseModel):
    package_item_id: str
    package_id: int

class Feature(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str
    
class Equipment(BaseModel):
    equipment_name: str
    equipment_id: str
    marker_icon_url: str
    marker_icon_colour: str
    
class EquipmentType(BaseModel):
    equipment_type_name: str

class ContactSale(BaseModel):
    phone: str
    call_time:str
    user_id:int

class Onboarding(BaseModel):
    asset_type_id: int 
    no_of_assets: int
    package_id: int
    user_id: int

class Asset(BaseModel):
    user_id: int
    asset_type_id: int
    asset_name: str
    equipment_id: int
    vin_no: str

class Equipment:
    equipment_name:str
    equipment_type_id: int
    marker_icon_url: str
    marker_icon_color: str

class OnboardingFeatureAssignment:
    onboarding_id:int
    feature_id: int

class EquipmentType:
    equipment_type_name: str
    status: str

    


    





   
