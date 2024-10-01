from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator

from app.core import constants
from app.util.enums import (
    DeviceConfigurationVersion,
    DeviceStatus,
    PeripheralDeviceType,
    ActiveStatus
)


class CreatePeripheralDevice(BaseModel):
    device_type: PeripheralDeviceType
    no_of_devices: int

    @validator("no_of_devices")
    def check_no_of_devices(cls, value):
        if value <= 0:
            raise ValueError("The number of devices must be greater than 0")
        return value


class CreatePeripheralDeviceInput(BaseModel):
    device_type: PeripheralDeviceType
    serial_number: str


class CreateDeviceConfigurationInput(BaseModel):
    configuration_version: str
    configuration: dict


class GetDeviceConfiguration(BaseModel):
    key: str
    device_type: DeviceConfigurationVersion
    serial_number: str


class CreateGatewayDeviceConfiguration(BaseModel):
    configuration_version: DeviceConfigurationVersion
    upload_interval: int
    version: str
    host_name: str
    api_url: str
    token_url: str
    data_url: str
    alert_url: str
    configuration_url: str
    ssl_url: str
    wifi_ssid: Optional[str] = None
    wifi_password: Optional[str] = None
    wifi_static_ip: Optional[str] = None
    wifi_gateway: Optional[str] = None
    wifi_subnet: Optional[str] = None
    hide_wifi: Optional[bool] = None


class CreateGasNodeConfiguration(BaseModel):
    threshold_1: float
    threshold_2: float
    threshold_3: float


class CreatePyroNodeConfiguration(BaseModel):
    target_temperature_threshold: float
    ambient_temperature_threshold: float
    humidity_threshold: float
    air_quality_threshold: float
    critical_mxl_velocity: float
    critical_ambient_temperature: float
    critical_humidity_velocity: float
    critical_air_quality_velocity: float
    critical_mxl_acceleration: float
    critical_ambient_temperature_acceleration: float
    critical_humidity_acceleration: float
    critical_air_quality_acceleration: float


class CreateNodeConfiguration(BaseModel):
    configuration_version: DeviceConfigurationVersion
    description: str
    microprocessor_unit: str
    sensors: list
    physical_quantity: list
    update_interval: int
    battery_cutoff: float
    observation_time: float
    gas_node_configuration: Optional[CreateGasNodeConfiguration] = None
    pyro_node_configuration: Optional[CreatePyroNodeConfiguration] = None


class UpdatePeripheralDevice(BaseModel):
    location: str
    serial_number: str


class DeviceAlertRecipient(BaseModel):
    node_id: str
    user_uuids: list[UUID]


class DeviceAlertRecipientInput(BaseModel):
    node_id: str
    user_uuid: UUID


class UpdatePeripheralDeviceFull(UpdatePeripheralDevice):
    user_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None
    building_uuid: str
    installed_at: datetime = datetime.now()
    status: DeviceStatus = DeviceStatus.ASSIGNED


class DefaultPyroConfig(BaseModel):
    ambient_temperature_threshold: int = constants.PYRO_AMBIENT_TEMPERATURE_THRESHOLD
    humidity_threshold: int = constants.PYRO_HUMIDITY_THRESHOLD
    target_temperature_threshold: int = constants.PYRO_TARGET_TEMPERATURE_THRESHOLD
    flammable_smoke_threshold: float = constants.PYRO_FLAMMABLE_SMOKE_THRESHOLD
    minimum_threshold: int = 0
    peripheral_device_uuid: str


class DefaultGasConfig(BaseModel):
    ambient_temperature_threshold: int = 0
    humidity_threshold: int = 0
    target_temperature_threshold: int = 0
    flammable_smoke_threshold: float = 0
    minimum_threshold: int = constants.GAS_DEVICE_MINIMUM_THRESHOLD
    peripheral_device_uuid: str


class UpdateDeviceConfigThreshold(BaseModel):
    ambient_temperature_threshold: Optional[int] = None
    humidity_threshold: Optional[int] = None
    target_temperature_threshold: Optional[int] = None
    flammable_smoke_threshold: Optional[float] = None
    minimum_threshold: Optional[int] = None


class CreateGasCylinder(BaseModel):
    building_uuid: str
    cylinder_name: str
    cylinder_type_uuid: str


class CreateGasCylinderFull(BaseModel):
    user_uuid: str
    business_profile_uuid: str
    building_uuid: str
    cylinder_name: str
    cylinder_type_uuid: str


class LinkGasCylinderToDevice(BaseModel):
    gas_cylinder_uuid: Optional[str] = None
    gas_cylinder: Optional[CreateGasCylinder] = None
    serial_number: str






class CreateBuildingWithDevice(BaseModel):
    building_name: str
    longitude: float
    latitude: float
    image_url: str
    device_type: PeripheralDeviceType
    serial_number: str
    location: str


class CreateBuildingWithDeviceFull(BaseModel):
    building_name: str
    longitude: float
    latitude: float
    image_url: str
    user_uuid: str
    status : ActiveStatus = ActiveStatus.ACTIVE
    business_profile_uuid:Optional[str] = None


class UpdateBuildingWithDevice(BaseModel):
    building_uuid: str
    location: str
    status: DeviceStatus = DeviceStatus.ASSIGNED



