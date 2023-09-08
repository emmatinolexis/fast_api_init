from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class User(BaseModel):
    id: Optional[int]
    phone_number: PhoneNumber
    email_address: EmailStr
    password: str

    class Config:
        orm_model = True
