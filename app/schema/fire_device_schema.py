from pydantic import BaseModel

from app.util.enums import DeviceStatus, DeviceType


class UploadFireDevice(BaseModel):
    device_name: str
    serial_number: str
    device_type: DeviceType


class CreateFireDevice(BaseModel):
    serial_number: str
    location: str
    device_type: DeviceType


class CreateFireDevicePayload(CreateFireDevice):
    building_uuid: str
    user_uuid: str
    business_profile_uuid: str = None
    status: DeviceStatus = DeviceStatus.ASSIGNED
