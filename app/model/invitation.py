import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import RoleType


class Invitation(BaseModel):
    __tablename__ = "invitations"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=False,index=True
    )
    email = Column(String, unique=True, nullable=False,index=True)
    role_uuid = Column(UUID(as_uuid=True), ForeignKey("roles.uuid"),index=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    expired_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(25), nullable=False,index=True)
    invitation_type = Column(Enum(RoleType), nullable=False,index=True)
    business_profile = relationship("BusinessProfile", back_populates="invitations")
    role = relationship("Role")
