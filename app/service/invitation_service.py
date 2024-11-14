from datetime import datetime
from typing import List

from fastapi import Request
from pydantic import EmailStr

from app.core import activity_log_constants
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.repository.activity_log_repository import ActivityLogRepository
from app.repository.team_member_invitation_repository import (
    TeamMemberInvitationRepository,
)
from app.schema.activity_log_schema import ActivityLogSchema
from app.schema.invitation_schema import InvitationPayload
from app.service.base_service import BaseService
from app.util.enums import ActivityLogClass, ActivityLogType, InvitationStatus


class InvitationService(BaseService):
    def __init__(
        self,
        invitation_repository: TeamMemberInvitationRepository,
        activity_log_repository: ActivityLogRepository,
    ):
        self.invitation_repository = invitation_repository
        self.activity_log_repository = activity_log_repository
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
        role_uuids: List[str] = None,
        status: InvitationStatus = None,
    ):
        return self.invitation_repository.get_user_invitations(
            business_uuid, page, page_size, search, role_uuids, status
        )

    def get_all_admin_invites(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuids: list[str] = None,
        status=None,
    ):
        return self.invitation_repository.get_admin_invitations(
            page, page_size, email, role_uuids, status
        )

    def update_invitation_expiry(self, invitation_uuid: str, expiry_date: datetime):
        return self.invitation_repository.update_attr_by_uuid(
            invitation_uuid, "expired_at", expiry_date
        )

    def delete_invitation(
        self, invitation_uuid: str, current_user: User, request: Request
    ):
        try:
            self.invitation_repository.delete_by_uuid(invitation_uuid)

            activity_log = ActivityLogSchema(
                user_uuid=str(current_user.uuid),
                business_profile_uuid=str(current_user.business_profile_uuid)
                if current_user.business_profile_uuid
                else None,
                activity_title=activity_log_constants.DELETE_INVITATION,
                activity_type=ActivityLogType.DELETE_INVITATION,
                activity_class=ActivityLogClass.ADMIN,
                activity_description=activity_log_constants.DELETE_INVITATION_DESC.format(
                    full_name=current_user.first_name + " " + current_user.last_name
                ),
                ip_address=request.client.host,
            )

            self.activity_log_repository.create(schema=activity_log)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e
