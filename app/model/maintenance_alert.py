import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ServiceStatus


class MaintenanceAlert(BaseModel):
    __tablename__ = "maintenance_alerts"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False)
    alert_policy_uuid = Column(UUID(as_uuid=True), ForeignKey("alert_policies.uuid"), nullable=False)
    business_profile_uuid = Column(UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    status = Column(Enum(ServiceStatus), nullable=False, index=True)
