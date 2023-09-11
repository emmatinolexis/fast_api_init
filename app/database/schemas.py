from typing import Optional
from typing import Annotated, Union

from pydantic import (BaseModel, EmailStr, field_validator)
import re

class User(BaseModel):
    id: Optional[int]
    phone_number: Optional[str]
    email_address: Optional[EmailStr]
    password: str

    # @field_validator("phone_number")
    # @classmethod
    # def validate_international_phone_number(cls, phone_number:str):
    #         pattern = r'^\+\d{1,15}$'   
    #         if re.match(pattern, phone_number) == None:
    #             raise ValueError("Phone Number Should Be In International Format")
    #         return phone_number
    
    # class Config:
    #     orm_model = True
        
        
class LoginUser(BaseModel):
    phone_number: Optional[str]
    email_address: str
    password: str
    

class TokenData(BaseModel):
    email_addres: Union[EmailStr, None] = None
 
