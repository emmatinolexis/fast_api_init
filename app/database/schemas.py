from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import constr
from pydantic_extra_types.phone_numbers import PhoneNumber


class User(BaseModel):
    phone_number: PhoneNumber
    email_address: EmailStr
    password: constr(min_length=8,max_length=30)

    class Config:
        orm_model = True
        

class AssetType(BaseModel):
    asset_type_name: str
    asset_type_status: str

    class Config:
        orm_model = True

class Asset(BaseModel):
    asset_name: str
    asset_type_id: int
    asset_status: str
    user_id: str
    class Config:
        orm_model = True
        
