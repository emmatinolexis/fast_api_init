from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr


class Device(BaseModel):
    device_uuid: UUID
    quantity: int


class Address(BaseModel):
    address_name: str
    lat: int
    lng: int


class ShippingAddress(BaseModel):
    country: str
    first_name: str
    last_name: str
    address: Address
    post_code: Optional[str] = None
    city: str
    email: EmailStr
    phone: constr(max_length=15)


class OrderPayload(BaseModel):
    devices: List[Device]
    shipping_address: ShippingAddress
    payment_reference: str
    total_amount: int
