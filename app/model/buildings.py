import uuid

from sqlalchemy import Column, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class Building(BaseModel):
    __tablename__ = "buildings"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    building_name = Column(String(length=50), nullable=False, index=True)
    location = Column(String(length=100), nullable=False, index=True)
    image_url = Column(String(length=200), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)

