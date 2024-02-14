from uuid import UUID
from app.core import messages

from pydantic import EmailStr

from app.core.exceptions import NotFoundError
from app.repository.user_repository import UserRepository
from app.repository.business_profile_repository import BusinessProfileRepository
from app.repository.team_member_invitation_repository import TeamMemberInvitationRepository
from app.schema.invitation_schema import InvitationCreatePayload, InvitationPayload
from app.schema.user_schema import (
    AccountDeactivationPayload,
    UpdateUserPayload,
    UserPayload,
)
from app.service.base_service import BaseService
from app.util.enums import InvitationStatus


class UserService(BaseService):
    def __init__(
            self,
            user_repository: UserRepository,
            business_repository: BusinessProfileRepository,
            invitation_repository: TeamMemberInvitationRepository,
    ):
        self.user_repository = user_repository
        self.business_repository = business_repository
        self.invitation_repository = invitation_repository
        super().__init__(user_repository)

    def create_user(self, payload: UserPayload):
        return self.user_repository.create_user(payload)

    def update_user_by_uuid(self, uuid: str, payload: UpdateUserPayload):
        try:
            # check uuid is valid
            if not UUID(uuid):
                return None
            user = self.user_repository.update_user_by_uuid(uuid, payload)
            return user if user else None
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def get_user_by_email_address(self, email: EmailStr):
        try:
            user = self.user_repository.get_user_by_email_address(email)
            return user if user else None
        except Exception as e:
            raise e

    def update_user_status(self, uuid: str):
        try:
            user = self.user_repository.update_user_status(uuid)
            return user if user else None
        except Exception as e:
            raise e

    def change_password(
            self,
            user_uuid: str,
            old_password: str,
            new_password: str,
            password_confirmation: str,
    ):
        try:
            return self.user_repository.change_password(
                user_uuid, old_password, new_password, password_confirmation
            )

        except Exception as e:
            raise e

    def update_user_avatar(self, user_id: str, avatar_url: str):
        try:
            return self.user_repository.update_user_avatar(user_id, avatar_url)
        except Exception as e:
            raise e

    def create_team_member_invitation(self, uuid: str, payload: InvitationCreatePayload):
        business = self.business_repository.get_by_uuid(uuid)
        if not business:
            raise NotFoundError(detail=messages.BUSINESS_PROFILE_NOT_FOUND + str(uuid))

        return self.invitation_repository.create_invitation(
            payload=InvitationPayload(
                business_profile_uuid=business.uuid,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=payload.email,
                permissions=payload.permissions,
                status=InvitationStatus.PENDING,
                expired_at=None,
            )
        )

    def deactivate_user_account(self, uuid: str, payload: AccountDeactivationPayload):
        try:
            user = self.user_repository.deactivate_account(uuid, payload)
            return user if user else None
        except Exception as e:
            raise e
