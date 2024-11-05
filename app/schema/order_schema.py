from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr

from app.util.enums import OrderStatusRtd


class Device(BaseModel):
    inventory_uuid: UUID
    quantity: int


class OrderStatusSchema(BaseModel):
    order_status: OrderStatusRtd


class Address(BaseModel):
    address_name: str
    lat: float
    lng: float


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
    installation_request: Optional[bool] = False
