import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.model.permission import Permission
from app.model.role import Role


class RolePermissionAssignment(BaseModel):
    __tablename__ = "role_permission_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    role_uuid = Column(UUID(as_uuid=True), ForeignKey(Role.uuid), nullable=False)
    permission_uuid = Column(
        UUID(as_uuid=True), ForeignKey(Permission.uuid), nullable=False
    )
