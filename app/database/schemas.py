from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    phone_number: str
    email_address: str
    password: str

    class Config:
        orm_model = True
