from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ContactSaleStatus
from datetime import datetime


class ContactSale(BaseModel):
    phone_number: str
    call_time: datetime
    user_uuid: UUID
    status: ContactSaleStatus

    class Config:
        orm_model = True
