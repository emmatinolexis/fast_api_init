import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class AlertPolicyNotificationTypeAssignment(BaseModel):
    __tablename__ = "alert_policy_notification_type_assignment"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    alert_policy_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_policies.uuid"), nullable=False
    )
    alert_notification_type = Column(String(length=100), nullable=False, index=True)
