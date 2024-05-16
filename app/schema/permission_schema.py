from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import RoleType


class PermissionPayload(BaseModel):
    permission_name: str

    class Config:
        orm_model = True


class RolePayload(BaseModel):
    role_name: str
    role_type: RoleType
    permissions: List[UUID]

    class Config:
        orm_model = True


class RolePermissionAssignmentPayload(BaseModel):
    role_uuid: UUID
    permission_uuid: UUID

    class Config:
        orm_model = True
