import json
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schema.equipment_schema import Equipment, EquipmentType
from app.schema.marker_schema import MarkerIcon


class AssetTypeCreate(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str

    class Config:
        orm_model = True


class AssetType(BaseModel):
    asset_type_name: str
    description: str
    icon_url: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True


class Asset(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: str
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_no: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    equipment: Optional[Equipment] = None
    equipment_type: Optional[EquipmentType] = None
    asset_type: Optional[AssetType] = None
    marker_icon: MarkerIcon = None

    class Config:
        orm_model = True


class AssetCreate(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: str
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_no: Optional[str] = None
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
    asset_status: str
    equipment_type_uuid: Optional[UUID] = None
    vin_no: Optional[str] = None
    marker_icon_uuid: UUID
    marker_color: str
    equipment_uuid: UUID
    serial_no: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None

    class Config:
        orm_model = True


class AssetLocation(BaseModel):
    asset_uuid: UUID
    longitude: str
    latitude: str


class AssetLocationFetch(BaseModel):
    asset_uuid: UUID
    longitude: str
    latitude: str
    created_at: str


class Driver(BaseModel):
    asset_uuid: UUID
    first_name: str
    last_name: str
    phone_number: str
    license_url: str
    profile_picture_url: str


class AlertMaintenanceType(BaseModel):
    name: str
    status: str


class AlertMaintenanceTypeFetch(BaseModel):
    name: str
    status: str
    uuid: UUID
