import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class UserOrganisationAssignment(BaseModel):
    __tablename__ = "user_organisation_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=False
    )
