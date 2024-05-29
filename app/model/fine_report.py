import uuid

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import FineStatus, FineType


class FineReport(BaseModel):
    __tablename__ = "fine_reports"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False)
    incident_type = Column(Enum(FineType), nullable=False, index=True)
    reported_by = Column(String(length=50), nullable=False)
    fine_status = Column(Enum(FineStatus), nullable=False)
    fine_amount = Column(String(length=100), nullable=False)
    speed = Column(String(length=100), nullable=False)
    speed_time = Column(DateTime, nullable=False)
    speed_location = Column(JSON, nullable=False)
    asset = relationship("Asset")
