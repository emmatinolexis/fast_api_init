from typing import Optional
from typing import Annotated, Union

from pydantic import (BaseModel, EmailStr,field_validator)
import re

class User(BaseModel):
    id: Optional[int]
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    password: str
        
        
class LoginPayload(BaseModel):
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    password: str 
    
    class Config:
        orm_model = True
    

class TokenData(BaseModel):
    email_addres: Union[EmailStr, None] = None
 
