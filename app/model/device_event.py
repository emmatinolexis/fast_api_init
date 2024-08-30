import uuid

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.model.base_model import Base


class DeviceEvent(Base):
    __tablename__ = "device_events"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    node_id = Column(String(100), nullable=False, index=True)
    node_description = Column(String(50), nullable=False, index=True)
    master_id = Column(String(50), nullable=False, index=True)
    measurements = Column(JSON, nullable=False)
    event_datetime = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    class Config:
        orm_mode = True
