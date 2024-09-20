from typing import Optional

from pydantic import BaseModel, validator

from app.util.enums import PeripheralDeviceType


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
    device_type: PeripheralDeviceType
    configuration: dict


class GetDeviceConfiguration(BaseModel):
    key: str
    device_type: str
    serial_number: str


class CreateGatewayDeviceConfiguration(BaseModel):
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


class CreateNodeConfiguration(BaseModel):
    description: str
    microprocessor_unit: str
    sensors: list
    physical_quantity: list
    update_interval: int
    battery_cutoff: float
    observation_time: float
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


class UpdatePeripheralDevice(BaseModel):
    location: str
    serial_number: str


class UpdatePeripheralDeviceFull(UpdatePeripheralDevice):
    user_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None
    building_uuid: str
