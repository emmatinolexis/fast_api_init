import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus, DriverType


class Driver(BaseModel):
    __tablename__ = "drivers"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(
        UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=True, index=True
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=True,
        index=True,
    )
    driver_type = Column(Enum(DriverType), nullable=False)
    first_name = Column(String(length=30), nullable=False)
    last_name = Column(String(length=30), nullable=False, index=True)
    email = Column(String(length=50), nullable=False, index=True, unique=True)
    status = Column(Enum(ActiveStatus), nullable=False)
    phone_number = Column(String(length=20), nullable=True, unique=True, index=True)
    license_url = Column(String(length=100), nullable=True, index=True)
    profile_picture_url = Column(String(length=100), nullable=True, index=True)
    asset = relationship("Asset", uselist=False, back_populates="driver")
