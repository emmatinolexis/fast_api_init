import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


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
    geofence_type = Column(String(length=100), nullable=True, index=True)
    policy_name = Column(String(length=100), nullable=False, index=True)
    minimum_idle_time = Column(String(length=100), nullable=True, index=True)
    maintenance_alert_schedule = Column(String(length=100), nullable=True, index=True)
    maintenance_alert_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_maintenance_types.uuid"), nullable=True
    )
    alert_policy_type = relationship("AlertPolicyType", uselist=False, lazy="subquery")
    maintenance_alert_type = relationship("AlertMaintenanceType", lazy="subquery")
