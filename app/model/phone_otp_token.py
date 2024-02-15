import uuid
from xmlrpc.client import DateTime

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class PhoneOtpToken(BaseModel):
    __tablename__ = "phone_otp_tokens"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid"),
        primary_key=True,
    )
    token = Column(String, unique=True, nullable=False)
    expired_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="phone_otp_token")
