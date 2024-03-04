from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, conint
from pydantic_extra_types.coordinate import Latitude, Longitude

from app.schema.equipment_schema import EquipmentPayload, EquipmentTypePayload
from app.schema.marker_schema import MarkerIconPayload
from app.util.enums import ActiveStatus, AssetDeviceRequestStatus, AssetStatus


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
    vehicle_license_no: Optional[str] = None
    marker_color: Optional[str] = None
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
    vehicle_license_no: Optional[str] = None
    asset_status: AssetStatus
    equipment_type_uuid: Optional[UUID] = None
    device_imei: Optional[str] = None
    vin: Optional[str] = None
    marker_color: Optional[str] = None
    equipment_uuid: UUID
    serial_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    add_driver: bool = False
    driver_uuid: Optional[UUID] = None

    class Config:
        orm_model = True


class AssetInput(BaseModel):
    user_uuid: UUID
    asset_type_uuid: UUID
    asset_name: str
    asset_status: AssetStatus
    equipment_type_uuid: Optional[UUID] = None
    device_imei: Optional[str] = None
    vin: Optional[str] = None
    vehicle_license_no: Optional[str] = None
    marker_color: Optional[str] = None
    equipment_uuid: UUID
    serial_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None


class AssignDeviceInputPayload(BaseModel):
    device_imei: str

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
    asset_uuid: Optional[UUID] = None
    user_uuid: UUID
    business_uuid: Optional[UUID] = None
    first_name: str
    last_name: str
    phone_number: str
    license_url: str
    profile_picture_url: str


class AlertMaintenanceTypePayload(BaseModel):
    name: str
    status: ActiveStatus


class AssetDeviceRequest(BaseModel):
    asset_type_uuid: UUID
    number_of_assets: conint(ge=1)
    metrics: List[str]


class CreateAssetDeviceRequestPayload(AssetDeviceRequest):
    user_uuid: str
    status: AssetDeviceRequestStatus = AssetDeviceRequestStatus.PENDING
