from typing import Optional

from pydantic import BaseModel

from app.util.enums import DeviceType


class UploadFireDevice(BaseModel):
    device_name: str
    serial_number: str
    device_type: DeviceType
