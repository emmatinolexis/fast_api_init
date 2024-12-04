import uuid

from sqlalchemy import Column, Double, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import IncidenceType, IncidentStatus


class Incident(BaseModel):
    __tablename__ = "incidents"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    incident_type = Column(Enum(IncidenceType), nullable=False, index=True)
    longitude = Column(Double, nullable=False, index=True)
    latitude = Column(Double, nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    status = Column(Enum(IncidentStatus), nullable=True,default=IncidentStatus.UNVERIFIED)

    def dto(self):
        return {
            "id": self.id,
            "incidentType": self.incident_type,
            "userId": self.user_uuid,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
