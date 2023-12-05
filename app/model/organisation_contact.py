import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class OrganisationContact(BaseModel):
    __tablename__ = "organisation_contacts"
    uuid = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        primary_key=True
    )
    first_name = Column(String(length=100), nullable=False, index=True)
    last_name = Column(String(length=100), nullable=False, index=True)
    role = Column(String(length=100), nullable=False, index=True)
    country = Column(String(length=100), nullable=True, index=True)
    message = Column(String(length=255), nullable=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User")
