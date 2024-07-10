import uuid

from sqlalchemy import JSON, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.alert_policy import AlertPolicy
from app.model.asset import Asset
from app.model.base_model import BaseModel
from app.model.business_profile import BusinessProfile
from app.model.user import User


class AlertPolicyViolation(BaseModel):
    __tablename__ = "alert_policy_violations"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    alert_policy_uuid = Column(
        UUID(as_uuid=True), ForeignKey(AlertPolicy.uuid), nullable=False
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey(Asset.uuid), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey(BusinessProfile.uuid), nullable=True
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    violation_coordinates = Column(JSON, nullable=False)
    status = Column(String(length=20), nullable=False)
    violation_time = Column(Float, nullable=False, default=0)
    violation_distance = Column(Float, nullable=False, default=0)
    asset = relationship("Asset")
    alert_policy = relationship("AlertPolicy")
    user = relationship("User")
    business_profile = relationship("BusinessProfile")
