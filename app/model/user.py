import uuid
from enum import Enum

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import AccountType, UserRole


class User(BaseModel):
    __tablename__ = "users"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(length=30), nullable=False, index=True)
    last_name = Column(String(length=30), nullable=False, index=True)
    phone_number = Column(String(length=20), nullable=True, unique=True, index=True)
    email_address = Column(String(length=100), nullable=False, unique=True, index=True)
    password = Column(String(length=200), nullable=False)
    verifiedAt = Column(String(length=100), nullable=True, default=None, index=True)
    location = Column(String(length=30), nullable=True, index=True)
    address = Column(String(length=50), nullable=True, index=True)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    role = Column(
        Enum(UserRole), nullable=False, default=UserRole.CUSTOMER.value, index=True
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    business_profile = relationship(
        "BusinessProfile", uselist=False, back_populates="users"
    )
    user_verification = relationship(
        "EmailVerification", uselist=False, back_populates="user"
    )
