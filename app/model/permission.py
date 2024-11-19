import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import PermissionType


class Permission(BaseModel):
    __tablename__ = "permissions"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    permission_name = Column(String(70), unique=True, nullable=False,index=True)
    model = Column(String(100), unique=False, nullable=False)
    permission_type = Column(Enum(PermissionType), nullable=False,index=True)
    roles = relationship(
        "Role", secondary="role_permission_assignments", back_populates="permissions"
    )
