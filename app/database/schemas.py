from typing import Optional
from typing import  Union

from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
#from pydantic import Field
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    id: Optional[int]
    username: str
    phone_number: Optional[PhoneNumber] = None
    email_address: Optional[EmailStr] = None
    password: str #Add Data validation to constrain password length between
                  #a length of 8 and 30. constr and Field not working as expected
                  
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
 






   