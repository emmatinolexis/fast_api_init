import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class Driver(BaseModel):
    __tablename__ = "drivers"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=False
    )
    first_name = Column(String(length=30), nullable=False, index=True)
    last_name = Column(String(length=30), nullable=False, index=True)
    phone_number = Column(String(length=20), nullable=True, unique=True, index=True)
    license_url = Column(String(length=100), nullable=True, index=True)
    profile_picture_url = Column(String(length=100), nullable=True, index=True)
