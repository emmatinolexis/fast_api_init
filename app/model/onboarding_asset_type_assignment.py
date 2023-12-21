import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class OnboardingAssetTypeAssignment(BaseModel):
    __tablename__ = "onboarding_asset_type_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    onboarding_uuid = Column(
        UUID(as_uuid=True), ForeignKey("onboardings.uuid"), nullable=False
    )
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("asset_types.uuid"), nullable=False
    )
