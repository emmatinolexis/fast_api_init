from pydantic import BaseModel

from app.util.enums import CrowdIncidentType


class IncidentPayload(BaseModel):
    incident_type: CrowdIncidentType
    longitude: float
    latitude: float
