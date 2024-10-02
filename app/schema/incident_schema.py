from pydantic import BaseModel

from app.util.enums import IncidenceType


class IncidentPayload(BaseModel):
    incident_type: IncidenceType
    longitude: float
    latitude: float
    user_uuid: str
