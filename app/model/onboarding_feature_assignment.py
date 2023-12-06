import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class OnboardingFeatureAssignment(BaseModel):
    __tablename__ = "onboarding_feature_assignments"
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
    feature_uuid = Column(
        UUID(as_uuid=True), ForeignKey("features.uuid"), nullable=False
    )
