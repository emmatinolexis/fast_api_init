import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import IncidentStatus, IncidentType


class TheftIncidence(BaseModel):
    __tablename__ = "theft_incidence"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False,index=True)
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False,index=True)
    incident_type = Column(Enum(IncidentType), nullable=False)
    status = Column(Enum(IncidentStatus), nullable=False,index=True)

    user = relationship("User", back_populates="theft_incidents")
    asset = relationship("Asset", uselist=False)
