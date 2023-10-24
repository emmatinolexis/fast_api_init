from typing import Optional
from typing import  Union

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    first_name: str
    last_name: str
    location: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]
    email_address: EmailStr
    password: str
    verification_token: Optional[str]
    google_auth: str 
    verifiedAt: Optional[str] = "null"
    
class UserLogin(BaseModel):
    email_address: EmailStr
    password: str
    
class EmailVerfication(BaseModel):
    email: str
    
class AssetType(BaseModel):
    asset_type_name: str
    status: str
    class Config:
        orm_model = True

class Asset(BaseModel):
    asset_name: str
    asset_id: int
    asset_status: str
    user_id: str
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
 






   
