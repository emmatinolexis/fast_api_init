from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import constr
from pydantic_extra_types.phone_numbers import PhoneNumber


class User(BaseModel):
    id: Optional[int]
    phone_number: PhoneNumber
    email_address: EmailStr
    password: constr(min_length=8,max_length=30)

    class Config:
        orm_model = True
