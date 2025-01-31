import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import SubscriptionStatus, SubscriptionPeriod, SubscriptionTypes


class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    subscription_type = Column(Enum(SubscriptionTypes), nullable=False, index=True)
    subscription_period = Column(Enum(SubscriptionPeriod), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    subscription_amount = Column(Integer, nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    package_uuid = Column(
        UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=False
    )
    status = Column(Enum(SubscriptionStatus), nullable=False)
    user = relationship("User")
    package = relationship("Package")
