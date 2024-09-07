from pydantic import BaseModel
from app.util.enums import IncidentType


class IncidentPayload(BaseModel):
    incident_type : IncidentType
    longitude: float
    latitude: float

