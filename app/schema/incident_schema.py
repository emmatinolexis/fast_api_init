from typing import List

from pydantic import BaseModel, Field

from app.util.enums import IncidenceType


class IncidentPayload(BaseModel):
    incident_type: IncidenceType
    longitude: float
    latitude: float
    user_uuid: str
