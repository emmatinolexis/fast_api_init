from datetime import datetime, timedelta
from uuid import UUID

from pydantic import EmailStr

from app.core import messages
from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.core.exceptions import NotFoundError
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.team_member_invitation_repository import (
    TeamMemberInvitationRepository,
)
from app.repository.user_repository import UserRepository
from app.repository.user_subscription_repository import UserSubscriptionRepository
from app.schema.invitation_schema import (
    InvitationCreatePayloadSingle,
    InvitationPayload,
)
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
        user_subscription_repository: UserSubscriptionRepository,
        invitation_repository: TeamMemberInvitationRepository,
        subscription_repository: SubscriptionRepository,
    ):
        self.user_repository = user_repository
        self.invitation_repository = invitation_repository
        self.user_subscription_repository = user_subscription_repository
        self.subscription_repository = subscription_repository
        super().__init__(user_repository)

    def create_user(self, payload: UserPayload):
        return self.user_repository.create_user(payload)

    def get_account_users(self, business_uuid: str):
        return self.user_repository.get_account_users(business_uuid)

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

    def get_user_by_uuid(self, user_uuid: str):
        try:
            user = self.user_repository.get_user_by_uuid(user_uuid)

            user_plan = self.user_subscription_repository.get_user_subscription(
                user.get("email_address")
            )

            if user_plan:
                paystack_subscription = (
                    self.subscription_repository.get_paystack_subscription(
                        user_plan.subscription_code
                    )
                )

                user_package = {
                    "package_name": paystack_subscription["plan"]["name"],
                    "package_items": paystack_subscription["package_items"],
                }
                # return user_package
            else:
                user_package = {
                    "package_name": FREE_PACKAGE,
                    "package_items": FREE_PACKAGE_ITEMS,
                }

            user["package"] = user_package

            return user if user else None

        except Exception as e:
            raise e

    def check_business_exists(self, name, email, phone):
        try:
            business = self.user_repository.check_business_exists(name, email, phone)
            return business if business else None
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

    def create_team_member_invitation(
        self, uuid: str, payload: InvitationCreatePayloadSingle, user: dict
    ):
        if not user.business_profile_uuid:
            raise NotFoundError(detail=messages.BUSINESS_PROFILE_NOT_FOUND + str(uuid))

        try:
            return self.invitation_repository.create_invitation(
                payload=InvitationPayload(
                    business_profile_uuid=str(user.business_profile_uuid),
                    email=payload.email,
                    role_uuid=payload.role_uuid,
                    status=InvitationStatus.PENDING,
                    expired_at=datetime.now() + timedelta(days=3),
                )
            )
        except Exception as e:
            raise e

    def deactivate_user_account(self, uuid: str, payload: AccountDeactivationPayload):
        try:
            user = self.user_repository.deactivate_account(uuid, payload)
            return user if user else None
        except Exception as e:
            raise e

    def get_user_by_phone_number(self, phone_number: str):
        try:
            return self.user_repository.get_user_by_phone_number(phone_number)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e
