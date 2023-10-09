from typing import Optional
from typing import  Union

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    username: Optional[str]
    phone_number: Optional[str]
    email_address: EmailStr
    password: str
    verifiedAt: Optional[str]
    
class UserLogin(BaseModel):
    email_address: EmailStr
    password: str
    
class EmailVerification(BaseModel):
    email_address: str
    
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

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    
class VerifyToken(BaseModel):
    Token: str
    
class LoginPayload(BaseModel):
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    password: str 

    class Config:
        orm_model = True

class TokenData(BaseModel):
    username: Union[str, None] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str
 






   
