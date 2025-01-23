import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import PaymentStatus, PaymentTypes


class Payment(BaseModel):
    __tablename__ = "payments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    reference_no = Column(String(length=100), nullable=True, index=True)
    amount = Column(String(length=100), nullable=False, index=True)
    status = Column(Enum(PaymentStatus), nullable=False, index=True)
    payment_type = Column(Enum(PaymentTypes), nullable=False, index=True)
    user_email = Column(
        String(length=50), ForeignKey("users.email_address"), nullable=False, index=True
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=False,
        index=True,
    )
    channel = Column(String(length=50), nullable=False, index=True)
    business_profile = relationship("BusinessProfile", back_populates="payments")
    user = relationship("User")
