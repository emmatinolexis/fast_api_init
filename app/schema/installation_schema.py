from datetime import date, time
from uuid import UUID
from pydantic import BaseModel
from typing import Any, Optional


class InstallationPayload(BaseModel):
    order_uuid: UUID
    date_of_installation: date
    time_of_installation: time


class AssignInstallerPayload(BaseModel):
    installation_uuid: UUID
    installer_uuid: UUID


class InstallationResponse(BaseModel):
    installation_uuid: str
    status: Optional[str]
    installer_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    location: Optional[Any] 
    date_of_installation: Optional[date]
    time_of_installation: Optional[time]
    devices: Optional[Any]

