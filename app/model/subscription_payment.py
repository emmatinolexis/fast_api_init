import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class SubscriptionPayment(BaseModel):
    __tablename__ = "subscription_payments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    subscription_uuid = Column(
        UUID(as_uuid=True), ForeignKey("subscriptions.uuid"), nullable=False
    )
    payment_uuid = Column(
        UUID(as_uuid=True), ForeignKey("payments.uuid"), nullable=False
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User")
    payment = relationship("Payment")
    subscription = relationship("Subscription")
