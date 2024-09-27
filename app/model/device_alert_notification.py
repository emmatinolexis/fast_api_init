import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class DeviceAlertNotification(BaseModel):
    __tablename__ = "device_alert_notifications"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("peripheral_devices.node_id"),
        nullable=False,
    )
    user_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid"),
        nullable=False,
    )
    user = relationship("User")
    peripheral_device = relationship("PeripheralDevice")
