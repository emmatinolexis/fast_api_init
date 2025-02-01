from datetime import time
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ContactSaleStatus


class ContactSale(BaseModel):
    phone_number: str
    call_time: time
    user_uuid: UUID
    status: ContactSaleStatus

    class ConfigDict:
        from_attributes = True
