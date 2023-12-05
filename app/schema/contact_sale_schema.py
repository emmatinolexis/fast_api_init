from uuid import UUID

from pydantic import BaseModel


class ContactSale(BaseModel):
    phone_number: str
    call_time: str
    user_uuid: UUID
    status: str

    class Config:
        orm_model = True
