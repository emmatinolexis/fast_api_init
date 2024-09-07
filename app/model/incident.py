import uuid

from app.model.base_model import BaseModel
from sqlalchemy import Column, Enum, Double, DateTime

from sqlalchemy.dialects.postgresql import UUID
from app.util.enums import CrowdIncidentType

class Incident(BaseModel):
    __tablename__ = "incident"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    incident_type = Column(Enum(CrowdIncidentType),nullable=False,index=True)
    longitude = Column(Double, nullable=False, index=True)
    latitude = Column(Double, nullable=False, index=True)
