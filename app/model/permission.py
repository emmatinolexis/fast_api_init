import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    permission_name = Column(String(100), unique=True, nullable=False)
    roles = relationship(
        "Role", secondary="role_permission_assignments", back_populates="permissions"
    )
