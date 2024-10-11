from datetime import datetime

from pydantic import EmailStr

from app.repository.team_member_invitation_repository import (
    TeamMemberInvitationRepository,
)
from app.schema.invitation_schema import InvitationPayload
from app.service.base_service import BaseService
from app.util.enums import InvitationStatus


class InvitationService(BaseService):
    def __init__(self, invitation_repository: TeamMemberInvitationRepository):
        self.invitation_repository = invitation_repository
        super().__init__(invitation_repository)

    def create_invitation(self, invitation: InvitationPayload):
        return self.invitation_repository.create_invitation(invitation)

    def get_invitation_by_email(self, email: EmailStr):
        return self.invitation_repository.get_invitation_by_email(email)

    def get_all_user_invites(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        search: str = None,
        role_uuid: str = None,
        status: InvitationStatus = None,
    ):
        return self.invitation_repository.get_user_invitations(
            business_uuid, page, page_size, search, role_uuid, status
        )

    def get_all_admin_invites(
        self, page=1, page_size=10, email: str = None, role_uuids: list[str] = None
    ):
        return self.invitation_repository.get_admin_invitations(
            page, page_size, email, role_uuids
        )

    def update_invitation_expiry(self, invitation_uuid: str, expiry_date: datetime):
        return self.invitation_repository.update_attr_by_uuid(
            invitation_uuid, "expired_at", expiry_date
        )
