from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.coordinate import Latitude, Longitude

from app.schema.equipment_schema import EquipmentPayload, EquipmentTypePayload
from app.schema.marker_schema import MarkerIconPayload
from app.util.enums import (
    ActiveStatus,
    AssetCreators,
    AssetDeviceRequestStatus,
    AssetStatus,
    AssetUsageType,
    DeviceType,
    DriverType,
    ImmobilizerReason,
    ImmobilizerType,
    IncidentStatus,
    IncidentType,
)


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
    image_url: Optional[str] = None
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
    business_profile_uuid: Optional[UUID] = None
    asset_type_uuid: UUID
    asset_name: str
    image_url: Optional[str] = None
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


class PatchAssetPayload(BaseModel):
    asset_name: Optional[str] = None
    image_url: Optional[str] = None


class ThirdPartyAssetPayload(BaseModel):
    usage_type: AssetUsageType
    vin: str
    vehicle_license_no: Optional[str] = None
    equipment_uuid: UUID
    make: Optional[str] = None
    model: Optional[str] = None
    image_url: str
    first_name: str
    last_name: str
    phone_number: str
    email_address: EmailStr
    residential_address: str


class ThirdPartyAssetInput(BaseModel):
    asset_type_uuid: UUID
    asset_status: AssetStatus
    usage_type: AssetUsageType
    created_by: AssetCreators
    vin: str
    vehicle_license_no: Optional[str] = None
    equipment_uuid: UUID
    make: Optional[str] = None
    model: Optional[str] = None
    image_url: str
    vehicle_owner_uuid: UUID


class VehicleOwnerInput(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email_address: str
    residential_address: str


class GasCylinderInput(BaseModel):
    cylinder_name: str
    # material_type: GasCylinderMaterialType
    cylinder_type_uuid: UUID
    device_serial_number: str


class GasCylinderPayload(BaseModel):
    cylinder_name: str
    # material_type: GasCylinderMaterialType
    cylinder_type_uuid: UUID
    gas_device_serial_number: str
    user_uuid: UUID
    building_uuid: UUID
    business_profile_uuid: UUID


class CreateBuildingInput(BaseModel):
    building_name: str
    longitude: float
    latitude: float
    image_url: str
    status: ActiveStatus
    user_uuid: UUID
    business_profile_uuid: Optional[UUID] = None


class CreateFireDeviceInput(BaseModel):
    serial_number: str
    building_uuid: UUID
    user_uuid: UUID
    business_profile_uuid: Optional[UUID] = None
    location: str
    device_type: DeviceType


class CreateFireDeviceInputAsset(BaseModel):
    serial_number: str
    location: str


class BuildingInput(BaseModel):
    building: Optional[CreateBuildingInput] = None
    building_uuid: Optional[UUID] = None
    create_gas: Optional[bool] = False
    create_building_without_cylinder: Optional[bool] = False
    gas_cylinder: Optional[GasCylinderInput] = None
    create_fire_device: Optional[bool] = False
    fire_device: Optional[CreateFireDeviceInputAsset] = None


class UpdateBuildingPayload(BaseModel):
    building_name: Optional[str] = None
    image_url: Optional[str] = None


class AssetInput(BaseModel):
    user_uuid: UUID
    business_profile_uuid: Optional[UUID] = None
    asset_type_uuid: UUID
    asset_name: str
    asset_status: AssetStatus
    image_url: Optional[str] = None
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
    sim_phone_number: str

    class Config:
        orm_model = True


class AssetLocationPayload(BaseModel):
    asset_uuid: UUID
    longitude: Longitude
    latitude: Latitude


class TheftIncidencePayload(BaseModel):
    asset_uuid: UUID
    user_uuid: UUID
    incident_type: IncidentType
    status: IncidentStatus


class TheftReportPayload(BaseModel):
    title: str
    report_details: str
    theft_incident_uuid: UUID
    user_uuid: UUID


class VehicleModelPayload(BaseModel):
    value: str
    title: str


class VehicleMakeInput(BaseModel):
    name: str


class VehicleModelInput(BaseModel):
    name: str
    vehicle_make_uuid: UUID


class VehicleMake(BaseModel):
    value: str
    title: str
    models: List[VehicleModelPayload]


class VehicleMakePayload(BaseModel):
    vehicle_makes: List[VehicleMake]


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
    driver_type: DriverType
    last_name: str
    email: str
    status: ActiveStatus
    phone_number: str
    license_url: str
    profile_picture_url: str


class AlertMaintenanceTypePayload(BaseModel):
    name: str
    status: ActiveStatus


class AssetDeviceRequest(BaseModel):
    asset_uuids: List[UUID]
    metrics: List[str]


class CreateAssetDeviceRequestPayload(AssetDeviceRequest):
    user_uuid: str
    status: AssetDeviceRequestStatus = AssetDeviceRequestStatus.PENDING


class ImmobilizerPayload(BaseModel):
    reason: ImmobilizerReason
    type: ImmobilizerType
    user_uuid: UUID
    asset_uuid: UUID


class EngineOnPayload(BaseModel):
    type: ImmobilizerType
    user_uuid: UUID
    asset_uuid: UUID
