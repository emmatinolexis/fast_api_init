import uuid

from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class UserSubscription(BaseModel):
    __tablename__ = "user_subscriptions"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_email = Column(
        String(length=100),
        ForeignKey("users.email_address"),
        nullable=False,
        index=True,
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=False
    )
    subscription_code = Column(String(length=50), nullable=True, index=True)
    # payment_reference = Column(String(length=50), nullable=True, index=True)
    plan_code = Column(String(length=50), nullable=False, index=True)git
    status = Column(String(length=50), nullable=False, index=True)
    next_payment_date = Column(String(length=50), nullable=True, index=True)
    plan = Column(JSON, nullable=True)
    user = relationship("User")
    business_profile = relationship("BusinessProfile", back_populates="subscriptions")
