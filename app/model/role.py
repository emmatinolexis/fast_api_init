import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import RoleType


class Role(BaseModel):
    __tablename__ = "roles"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    role_name = Column(String(100), unique=True, nullable=False)
    role_type = Column(Enum(RoleType), nullable=False)

    permissions = relationship(
        "Permission", secondary="role_permission_assignments", back_populates="roles"
    )
