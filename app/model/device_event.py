import uuid

from sqlalchemy import JSON, Column, DateTime, String, Boolean
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
    node_description = Column(String(50), nullable=True, index=True)
    gateway_id = Column(String(50), nullable=False, index=True)
    measurements = Column(JSON, nullable=False)
    event_datetime = Column(String(80), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    alert_type = Column(String(50), nullable=False, index=True)
    requires_attention = Column(Boolean, nullable=False, index=True)
    alert_description = Column(String(50), nullable=False, index=True)
    device_type = Column(String(50), nullable=False, index=True)

    class ConfigDict:
        from_attributes = True
