from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus, DeviceType


class SmsCommandPayload(BaseModel):
    immediate_shutdown_command: str = None
    immediate_on_command: str = None
    queued_shutdown_command: str = None
    queued_on_command: str = None

    class ConfigDict:
        from_attributes = True


class DevicePayload(BaseModel):
    device_manufacturer_uuid: UUID
    device_name: str
    description: str = None
    sim_phone_number: str = None
    device_serial_no: str
    image_url: Optional[str] = None
    assign_to_asset_status: str = None

    class ConfigDict:
        from_attributes = True


class DeviceManufacturerPayload(BaseModel):
    manufacturer_name: str
    shutdown_on_command: SmsCommandPayload
    status: ActiveStatus

    class ConfigDict:
        from_attributes = True


class ImeiAssignPayload(BaseModel):
    device_imei: str

    class ConfigDict:
        from_attributes = True


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

    class ConfigDict:
        from_attributes = True


class InventoryUpdatePayload(BaseModel):
    device_name: Optional[str] = None
    quantity: Optional[int] = None
    device_manufacturer_uuid: Optional[UUID] = None
    cost_price: Optional[int] = None
    selling_price: Optional[int] = None
    description: Optional[str] = None
    device_manufacturer_uuid: Optional[UUID] = None
    image: Optional[str] = None

    class ConfigDict:
        from_attributes = True
