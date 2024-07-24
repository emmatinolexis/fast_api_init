from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import DeviceStatus


class CreateGasDevice(BaseModel):
    device_name: str


class UserCreateGasDevice(BaseModel):
    device_name: str
    user_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None


class LinkGasCylinder(BaseModel):
    gas_device_uuid: Optional[UUID] = None


class UpdateGasDevice(BaseModel):
    status: DeviceStatus
