from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from pydantic import EmailStr

from app.core import messages
from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.core.exceptions import NotFoundError, UnAuthorizedError
from app.repository.asset_repository import AssetRepository
from app.repository.driver_license_repository import DriverLicenseRepository
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.team_member_invitation_repository import (
    TeamMemberInvitationRepository,
)
from app.repository.user_repository import UserRepository
from app.repository.user_subscription_repository import UserSubscriptionRepository
from app.schema.invitation_schema import (
    AdminInvitationPayload,
    InvitationCreatePayloadSingle,
    InvitationPayload,
)
from app.schema.user_schema import (
    AccountDeactivationPayload,
    DriverLicenseUpdates,
    DriversLicenseFull,
    UpdateUserPayload,
    UserPayload,
    UserProfileUdatePayload,
)
from app.service.base_service import BaseService
from app.transfomers.driver_transformer import driver_transformer
from app.util.enums import InvitationStatus, RoleType
from app.util.utils import parse_date


class UserService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
        user_subscription_repository: UserSubscriptionRepository,
        invitation_repository: TeamMemberInvitationRepository,
        subscription_repository: SubscriptionRepository,
        asset_repository: AssetRepository,
        driver_license_repository: DriverLicenseRepository,
    ):
        self.user_repository = user_repository
        self.invitation_repository = invitation_repository
        self.user_subscription_repository = user_subscription_repository
        self.subscription_repository = subscription_repository
        self.asset_reposoitory = asset_repository
        self.driver_license_repository = driver_license_repository
        super().__init__(user_repository)

    def create_user(self, payload: UserPayload):
        return self.user_repository.create_user(payload)

    def get_account_users(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        search: str = None,
        role_uuids: list = None,
        status: InvitationStatus = None,
    ):
        return self.user_repository.get_account_users(
            business_uuid, page, page_size, search, role_uuids, status
        )

    def update_user_by_uuid(self, uuid: str, payload: UpdateUserPayload):
        try:
            try:
                uuid_obj = UUID(uuid)
            except ValueError:
                return None

            if payload.license:
                self._handle_license_update(str(uuid_obj), payload)

            user = self.user_repository.update_user_by_uuid(uuid, payload)
            return user if user else None

        except (NotFoundError, UnAuthorizedError) as e:
            raise e

    def _handle_license_update(self, uuid: str, payload: UpdateUserPayload):
        try:
            existing_license = (
                self.driver_license_repository.get_license_by_license_number(
                    payload.license.license_number
                )
            )

            existing_user_license = (
                self.driver_license_repository.get_license_by_user_id(user_uuid=uuid)
            )

            if existing_license and existing_license.user_id != uuid:
                raise UnAuthorizedError(messages.LICENSE_IN_USE)

            if existing_user_license:
                self.driver_license_repository.update_by_uuid(
                    existing_user_license.uuid, payload.license
                )
                return

            if existing_license:
                self._update_existing_license(existing_license, uuid, payload)
            else:
                self._create_new_license(uuid, payload)

        except UnAuthorizedError as e:
            raise e
        except Exception as e:
            raise e

    def _update_existing_license(
        self, existing_license, uuid: str, payload: UpdateUserPayload
    ):
        if existing_license.user_id != uuid:
            raise UnAuthorizedError(messages.LICENSE_IN_USE)
        else:
            payload.license.expiration_date = parse_date(
                payload.license.expiration_date
            )
            self.driver_license_repository.update_by_uuid(
                uuid=existing_license.uuid, schema=payload.license
            )

    def _create_new_license(self, uuid: str, payload: UpdateUserPayload):
        new_license_data = DriversLicenseFull(
            license_number=payload.license.license_number,
            front_url=payload.license.front_url,
            back_url=payload.license.back_url,
            expiration_date=parse_date(payload.license.expiration_date),
            user_id=uuid,
        )
        self.driver_license_repository.create(new_license_data)

    def patch_user_by_uuid(self, uuid: str, payload: UserProfileUdatePayload):
        try:
            # check uuid is valid
            if not UUID(uuid):
                return None
            user = self.user_repository.patch_user_by_uuid(uuid, payload)
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
        new_password: str,
    ):
        try:
            return self.user_repository.change_password(user_uuid, new_password)

        except Exception as e:
            raise e

    def update_user_avatar(self, user_id: str, avatar_url: str):
        try:
            return self.user_repository.update_user_avatar(user_id, avatar_url)
        except Exception as e:
            raise e

    def create_team_member_invitation(
        self, uuid: str, payload: InvitationCreatePayloadSingle, user
    ):
        try:
            if not user.business_profile_uuid:
                raise NotFoundError(
                    detail=messages.BUSINESS_PROFILE_NOT_FOUND + str(uuid)
                )
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

    def create_admin_user_invitation(self, payload: InvitationCreatePayloadSingle):
        try:
            payload = AdminInvitationPayload(
                email=payload.email,
                role_uuid=payload.role_uuid,
                status=InvitationStatus.PENDING,
                expired_at=datetime.now() + timedelta(days=3),
                invitation_type=RoleType.ADMIN,
            )
            self.invitation_repository.create(payload)
            return payload
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

    def get_all_admin_team_members(
        self, page=1, page_size=10, email: str = None, role_uuid: str = None
    ):
        return self.user_repository.get_admin_team_members(
            page, page_size, email, role_uuid
        )

    def get_admin_team_member(self, team_member_uuid: str):
        try:
            return self.user_repository.get_admin_team_member(team_member_uuid)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def get_all_accounts(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        return self.user_repository.get_all_accounts(
            page, page_size, email, role_uuid, start_date, end_date
        )

    def get_drivers_by_business_uuid(
        self,
        business_uuid,
        role_uuid,
        page,
        page_size,
        operator_type: List[str] = None,
        status: str = None,
    ):
        return self.user_repository.get_drivers_by_business_uuid(
            business_uuid,
            role_uuid,
            page,
            page_size,
            operator_type=operator_type,
            status=status,
        )

    def get_driver_by_uuid(self, driver_uuid: str):
        driver = self.user_repository.get_driver_by_uuid(driver_uuid=driver_uuid)
        if driver is None:
            raise NotFoundError(messages.USER_NOT_FOUND + driver_uuid)
        return driver

    def change_operator_asset(
        self,
        asset_uuid: str,
        operator_uuid: str,
        user_uuid: str,
        business_profile_uuid: str = None,
    ):
        try:
            asset = self.asset_reposoitory.read_by_uuid(asset_uuid)
            if asset is None:
                raise NotFoundError(messages.NO_ASSET_FOUND)

            # Check if the asset's business profile matches the provided one
            if asset.business_profile_uuid != business_profile_uuid:
                # If not, check if the asset's user_uuid matches the provided user_uuid
                if asset.user_uuid != user_uuid:
                    raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            operator = self.user_repository.read_by_uuid(operator_uuid)
            if operator is None:
                raise NotFoundError(messages.NO_OPERATOR_FOUND)

            existing_asset_operator = (
                self.user_repository.get_user_by_assigned_asset_uuid(asset.uuid)
            )
            if existing_asset_operator is not None:
                self.user_repository.update_attr_by_uuid(
                    existing_asset_operator.uuid, "assigned_asset_uuid", None
                )

            self.user_repository.update_attr_by_uuid(
                operator.uuid, "assigned_asset_uuid", asset.uuid
            )

            return driver_transformer(operator, self.asset_reposoitory)

            # ... continue with the rest of your logic ...
        except Exception as e:
            raise e
