import uuid

from sqlalchemy import JSON, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import GeofenceShapeType, GeofenceType


class AlertPolicy(BaseModel):
    __tablename__ = "alert_policies"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    alert_policy_type_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("alert_policy_types.uuid"),
        nullable=False,
    )
    geofence_location_name = Column(String(length=100), nullable=True, index=True)
    geofence_type = Column(Enum(GeofenceType), nullable=True, index=True)
    geofence_shape_type = Column(Enum(GeofenceShapeType), nullable=True)
    geofence_coordinate_data = Column(JSON, nullable=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    policy_name = Column(String(length=100), nullable=False, index=True)
    minimum_idle_time = Column(String(length=100), nullable=True, index=True)
    maximum_speed_limit = Column(String(length=100), nullable=True)
    status = Column(String(length=20), nullable=False)
    maintenance_alert_schedule = Column(String(length=100), nullable=True, index=True)
    maintenance_alert_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_maintenance_types.uuid"), nullable=True
    )
    alert_policy_type = relationship("AlertPolicyType", uselist=False, lazy="subquery")
    maintenance_alert_type = relationship("AlertMaintenanceType", lazy="subquery")
    assets = relationship("Asset", secondary="alert_policy_asset_assignments")
    alert_recipients = relationship(
        "AlertNotificationAssignment", back_populates="alert_policy",cascade="all, delete-orphan"
    )
    alert_notification_types = relationship(
        "AlertPolicyNotificationTypeAssignment", back_populates="alert_policy",
    cascade="all, delete-orphan"
    )
    alert_policy_violations = relationship("AlertPolicyViolation")
