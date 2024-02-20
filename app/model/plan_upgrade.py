import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import SubscriptionPeriod, SubscriptionTypes


class PlanUpgrade(BaseModel):
    __tablename__ = "plan_upgrades"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    package_uuid = Column(
        UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=False
    )
    payment_uuid = Column(
        UUID(as_uuid=True), ForeignKey("payments.uuid"), nullable=True
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    subscription_type = Column(Enum(SubscriptionTypes), nullable=False, index=True)
    subscription_period = Column(Enum(SubscriptionPeriod), nullable=False, index=True)
    package = relationship("Package")
    payment = relationship("Payment")
