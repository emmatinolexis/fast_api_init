import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class GeofenceViolationTracker(BaseModel):
    __tablename__ = "geofence_violation_trackers"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    tracking_event_uuid = Column(
        UUID(as_uuid=True), ForeignKey("tracking_events.uuid"), nullable=False
    )
    alert_policy_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_policies.uuid"), nullable=False
    )
