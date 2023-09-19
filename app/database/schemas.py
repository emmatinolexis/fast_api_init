from typing import Optional
from typing import  Union

from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    id: Optional[int]
    phone_number: str
    email_address: EmailStr
    password: str

    class Config:
        orm_model = True
        

class AssetType(BaseModel):
    id: Optional[int]
    asset_type_name: str
    status: str

    class Config:
        orm_model = True

class Asset(BaseModel):
    id: Optional[int]
    asset_name: str
    asset_type_id: str
    asset_status: str
    customer_id: str
    class Config:
        orm_model = True
    username: str
    phone_number: Optional[PhoneNumber] = None
    email_address: Optional[EmailStr] = None
    password: str #Add Data validation to constrain password length between
                  #a length of 8 and 30. constr and Field not working as expected
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
 






   
