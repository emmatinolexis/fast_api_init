import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.model.onboarding_feature_assignment import OnboardingFeatureAssignment


class Onboarding(BaseModel):
    __tablename__ = "onboardings"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_type_uuid = Column(UUID(as_uuid=True), ForeignKey("asset_types.uuid"))
    number_of_assets = Column(String(length=50), nullable=False, index=True)
    number_of_months = Column(String(length=50), nullable=True, index=True)
    onboarding_type = Column(String(length=50), nullable=False, index=True)
    package_uuid = Column(
        UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=True
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User", uselist=False)
    package = relationship("Package", uselist=False)
    asset_type = relationship("AssetType", uselist=False)
    features = relationship(OnboardingFeatureAssignment, uselist=True)
