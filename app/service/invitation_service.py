from pydantic import EmailStr

from app.repository.team_member_invitation_repository import (
    TeamMemberInvitationRepository,
)
from app.schema.invitation_schema import InvitationPayload
from app.service.base_service import BaseService


class InvitationService(BaseService):
    def __init__(self, invitation_repository: TeamMemberInvitationRepository):
        self.invitation_repository = invitation_repository
        super().__init__(invitation_repository)

    def create_invitation(self, invitation: InvitationPayload):
        return self.invitation_repository.create_invitation(invitation)

    def get_invitation_by_email(self, email: EmailStr):
        return self.invitation_repository.get_invitation_by_email(email)
