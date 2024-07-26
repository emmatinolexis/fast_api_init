from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import DeviceStatus, GasCylinderMaterialType


class CreateGasDevice(BaseModel):
    device_name: str
    serial_number: str


class CreateGasCylinder(BaseModel):
    cylinder_name: str
    material_type: GasCylinderMaterialType
    user_uuid: str
    business_profile_uuid: Optional[str] = None
    gas_device_serial_number: Optional[str] = None


class CreateGasCylinderPayload(BaseModel):
    cylinder_name: str
    material_type: GasCylinderMaterialType
    gas_device_serial_number: Optional[str] = None
    cylinder_type_uuid: Optional[str] = None
    other_cylinder_type_uuid: Optional[str] = None


class CreateGasCylinderType(BaseModel):
    name: str
    image_url: str
    empty_weight: float
    full_weight: float


class CreateOtherCylinderType(BaseModel):
    name: str
    image_url: str
    empty_weight: float
    full_weight: float
    user_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None


class UserCreateGasDevice(BaseModel):
    device_name: str
    serial_number: str
    user_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None


class LinkGasCylinder(BaseModel):
    gas_device_uuid: Optional[UUID] = None


class UpdateGasDevice(BaseModel):
    device_name: Optional[str] = None
    status: Optional[DeviceStatus] = None


class GasEventPayload(BaseModel):
    device_serial_number: str
    current_weight: Optional[float] = None
    battery_level: Optional[float] = None
    event_timestamp: Optional[datetime] = None
