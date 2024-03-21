import uuid

from sqlalchemy import JSON, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.alert_policy import AlertPolicy
from app.model.asset import Asset
from app.model.base_model import BaseModel


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
    violation_coordinates = Column(JSON, nullable=False)
    asset = relationship("Asset")
    alert_policy = relationship("AlertPolicy")
