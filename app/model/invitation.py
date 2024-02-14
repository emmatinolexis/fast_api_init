import uuid

from app.model.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.util.enums import InvitationStatus


class Invitation(BaseModel):
    __tablename__ = 'invitations'
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('business_profiles.uuid')
    )
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    permissions = Column(JSON, nullable=False)
    accepted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    expired_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    status = Column(String(25), nullable=False, default=InvitationStatus.PENDING.value)
    business_profile = relationship('BusinessProfile', back_populates='invitations')
