from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude

from app.schema.equipment_schema import EquipmentPayload, EquipmentTypePayload
from app.schema.marker_schema import MarkerIconPayload
from app.util.enums import ActiveStatus, AssetStatus


class AssetTypePayload(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: ActiveStatus

    class Config:
        orm_model = True


class Asset(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: AssetStatus
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    equipment: Optional[EquipmentPayload] = None
    equipment_type: Optional[EquipmentTypePayload] = None
    asset_type: Optional[AssetTypePayload] = None
    marker_icon: MarkerIconPayload = None

    class Config:
        orm_model = True


class AssetPayload(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: AssetStatus
    equipment_type_uuid: Optional[UUID] = None
    vin: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    add_driver: bool = False
    driver_first_name: Optional[str] = None
    driver_last_name: Optional[str] = None
    driver_phone_number: Optional[str] = None
    driver_license_url: Optional[str] = None
    driver_profile_picture_url: Optional[str] = None

    class Config:
        orm_model = True


class AssetInput(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: AssetStatus
    equipment_type_uuid: Optional[UUID] = None
    vin: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None

    class Config:
        orm_model = True


class AssetLocationPayload(BaseModel):
    asset_uuid: UUID
    longitude: Longitude
    latitude: Latitude


class AssetLocationFetch(BaseModel):
    asset_uuid: UUID
    longitude: str
    latitude: str
    created_at: str


class DriverPayload(BaseModel):
    asset_uuid: UUID
    first_name: str
    last_name: str
    phone_number: str
    license_url: str
    profile_picture_url: str


class AlertMaintenanceTypePayload(BaseModel):
    name: str
    status: ActiveStatus
