from pydantic import BaseModel
from typing import Optional



class UploadFireDevice(BaseModel):
    device_name: str
    serial_number: str
