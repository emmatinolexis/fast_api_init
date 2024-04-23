from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr


class Device(BaseModel):
    device_uuid: UUID
    quantity: int


class ShippingAddress(BaseModel):
    country: str
    first_name: str
    last_name: str
    street_name: str
    post_code: str
    email: EmailStr
    phone: constr(max_length=15)


class OrderPayload(BaseModel):
    devices: List[Device]
    shipping_address: ShippingAddress
    payment_reference: str
