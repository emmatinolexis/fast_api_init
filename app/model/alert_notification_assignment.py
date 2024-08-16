import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class AlertNotificationAssignment(BaseModel):
    __tablename__ = "alert_notification_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    alert_policy_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("alert_policies.uuid", ondelete="CASCADE"),
        nullable=False,
    )
    recipient = Column(String(length=100), nullable=False, index=True)
    alert_policy = relationship("AlertPolicy", back_populates="alert_recipients")
