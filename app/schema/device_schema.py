from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus, DeviceType


class SmsCommandPayload(BaseModel):
    immediate_shutdown_command: str = None
    immediate_on_command: str = None
    queued_shutdown_command: str = None
    queued_on_command: str = None

    class Config:
        orm_model = True


class DevicePayload(BaseModel):
    device_manufacturer_uuid: UUID
    device_name: str
    description: str = None
    sim_phone_number: str = None
    device_serial_no: str
    image_url: Optional[str] = None
    assign_to_asset_status: str = None

    class Config:
        orm_model = True


class DeviceManufacturerPayload(BaseModel):
    manufacturer_name: str
    shutdown_on_command: SmsCommandPayload
    status: ActiveStatus

    class Config:
        orm_model = True


class ImeiAssignPayload(BaseModel):
    device_imei: str

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
