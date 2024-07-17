import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class AlertPolicyAssetAssignment(BaseModel):
    __tablename__ = "alert_policy_asset_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False)
    alert_policy_uuid = Column(
        UUID(as_uuid=True), ForeignKey("alert_policies.uuid"), nullable=False
    )
    status = Column(
        Enum(ActiveStatus), nullable=False, index=True, default=ActiveStatus.ACTIVE
    )
    asset = relationship("Asset", backref="alert_policy_assignments")
