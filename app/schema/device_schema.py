from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus, DeviceType


class DevicePayload(BaseModel):
    device_manufacturer_uuid: UUID
    device_name: str
    description: str = None
    device_serial_no: str
    user_uuid: Optional[UUID] = None
    business_profile_uuid: Optional[UUID] = None
    image_url: Optional[str] = None
    assign_to_asset_status: str = None

    class Config:
        orm_model = True


class DeviceManufacturerPayload(BaseModel):
    manufacturer_name: str
    status: ActiveStatus

    class Config:
        orm_model = True


class InventoryPayload(BaseModel):
    device_name: str
    description: str
    device_type: DeviceType
    quantity: int
    device_manufacturer_uuid: UUID
    cost_price: int
    description: str
    publish_on_site_status: bool
    images: List[str]

    class Config:
        orm_model = True
