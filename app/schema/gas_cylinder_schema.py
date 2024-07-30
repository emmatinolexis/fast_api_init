from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus, DeviceStatus, GasCylinderMaterialType


class CreateGasDevice(BaseModel):
    device_name: str
    serial_number: str


class UploadGasDeviceCSV(BaseModel):
    serial_number: str
    user_uuid: UUID


class CreateGasCylinder(BaseModel):
    cylinder_name: str
    material_type: GasCylinderMaterialType
    user_uuid: str
    business_profile_uuid: Optional[str] = None
    gas_device_serial_number: Optional[str] = None
    building_uuid: str


class CreateGasCylinderPayload(BaseModel):
    cylinder_name: str
    material_type: GasCylinderMaterialType
    gas_device_serial_number: Optional[str] = None
    cylinder_type_uuid: Optional[str] = None
    other_cylinder_type_uuid: Optional[str] = None
    building_uuid: str


class CreateGasCylinderOnly(BaseModel):
    cylinder_name: str
    material_type: GasCylinderMaterialType
    user_uuid: str
    business_profile_uuid: Optional[str] = None
    building_uuid: str


class CreateGasCylinderType(BaseModel):
    name: str
    empty_weight: float
    full_weight: float


class UpdateGasCylinderType(BaseModel):
    name: Optional[str] = None
    empty_weight: Optional[float] = None
    full_weight: Optional[float] = None
    status: Optional[ActiveStatus] = None


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


class GasCylinderEventResponse(BaseModel):
    id: int
