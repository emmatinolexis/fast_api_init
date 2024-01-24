import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class BusinessProfile(BaseModel):
    __tablename__ = "business_profiles"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    business_name = Column(String(length=100), nullable=False, unique=True, index=True)
    business_email = Column(String(length=100), nullable=False, unique=True, index=True)
    business_phone = Column(String(length=100), nullable=False, unique=True, index=True)
    business_location = Column(String(length=100), nullable=True, index=True)
    business_logo = Column(String(length=100), nullable=True, index=True)
    business_address = Column(String(length=100), nullable=True, index=True)
    users = relationship(
        "User",
        back_populates="business_profile",
    )
