from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus


class DevicePayload(BaseModel):
    device_manufacturer_uuid: UUID
    device_name: str
    description: str = None
    device_serial_no: str
    assign_to_asset_status: str = None

    class Config:
        orm_model = True


class DeviceManufacturerPayload(BaseModel):
    manufacturer_name: str
    status: str = ActiveStatus

    class Config:
        orm_model = True
