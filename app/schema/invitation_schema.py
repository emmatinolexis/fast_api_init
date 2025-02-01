from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from app.util.enums import InvitationStatus, RoleType


class Permissions(BaseModel):
    """Permissions granted for permissible items"""

    assets: List[str]
    users: List[str]
    reports: List[str]
    alerts: List[str]

    @field_validator("*")
    def validate_permissions(cls, attributes):
        valid_permissions = {"view", "create", "update", "delete"}
        for permission in attributes:
            if permission not in valid_permissions:
                raise ValueError(
                    f"Invalid permission {permission}. Must be one of {valid_permissions}"
                )

        return attributes


class InvitationCreatePayloadSingle(BaseModel):
    email: EmailStr
    role_uuid: UUID


class InvitationCreatePayload(BaseModel):
    invitations: List[InvitationCreatePayloadSingle]


class InvitationPayload(InvitationCreatePayloadSingle):
    business_profile_uuid: str
    status: InvitationStatus = InvitationStatus.PENDING
    expired_at: datetime

    class ConfigDict:
        from_attributes = True


class AdminInvitationPayload(InvitationCreatePayloadSingle):
    status: InvitationStatus = InvitationStatus.PENDING
    expired_at: datetime
    email: EmailStr
    role_uuid: UUID
    invitation_type: RoleType

    class ConfigDict:
        from_attributes = True
