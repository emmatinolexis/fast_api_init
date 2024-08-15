import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class AlertPolicyNotificationTypeAssignment(BaseModel):
    __tablename__ = "alert_policy_notification_type_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    alert_policy_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_policies.uuid",ondelete="CASCADE"), nullable=False
    )
    alert_notification_type = Column(String(length=100), nullable=False, index=True)
    alert_policy = relationship(
        "AlertPolicy", back_populates="alert_notification_types"
    )
