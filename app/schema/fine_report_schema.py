from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import FineStatus, FineType


class LocationPayload(BaseModel):
    longitude: float
    latitude: float


class FineReportPayload(BaseModel):
    asset_uuid: UUID
    incident_type: FineType
    reported_by: str
    fine_status: FineStatus
    speed: str
    speed_time: datetime
    speed_location: LocationPayload
    fine_amount: str

    class ConfigDict:
        from_attributes = True
