import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import Request
from pydantic import EmailStr

from app.core import messages

from app.core.exceptions import NotFoundError, UnAuthorizedError

from app.model.user import User

from app.repository.user_repository import UserRepository

from app.schema.invitation_schema import (
    AdminInvitationPayload,
    InvitationCreatePayloadSingle,
    InvitationPayload,
)
from app.schema.user_schema import (
    AccountDeactivationPayload,
    DriversLicenseFull,
    UpdateAdminTeamMemberPayload,
    UpdateUserPayload,
    UserPayload,
    UserProfileUdatePayload,
)
from app.service.base_service import BaseService

from app.util.enums import InvitationStatus, RoleType
from app.util.utils import calculate_percentage_change, parse_date


class UserService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository
        super().__init__(user_repository)

    async def create_user(self, payload: UserPayload):
        return await self.user_repository.create_user(payload)

    async def get_account_users(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        search: str = None,
        role_uuids: list = None,
        status: InvitationStatus = None,
        exclude_user_uuid: str = None,
    ):
        return await self.user_repository.get_account_users(
            business_uuid,
            page,
            page_size,
            search,
            role_uuids,
            status,
            exclude_user_uuid,
        )

    async def update_user_by_uuid(self, uuid: str, payload: UpdateUserPayload):
        try:
            try:
                uuid_obj = UUID(uuid)
            except ValueError:
                return None

            if payload.license:
                await self._handle_license_update(str(uuid_obj), payload)

            user = await self.user_repository.update_user_by_uuid(uuid, payload)
            return user if user else None

        except (NotFoundError, UnAuthorizedError) as e:
            raise e

    async def _handle_license_update(self, uuid: str, payload: UpdateUserPayload):
        try:
            existing_license = (
                await self.driver_license_repository.get_license_by_license_number(
                    payload.license.license_number
                )
            )

            existing_user_license = (
                await self.driver_license_repository.get_license_by_user_id(
                    user_uuid=uuid
                )
            )

            if existing_license and existing_license.user_id != uuid:
                raise UnAuthorizedError(messages.LICENSE_IN_USE)

            if existing_user_license:
                await self.driver_license_repository.update_by_uuid(
                    existing_user_license.uuid, payload.license
                )
                return

            if existing_license:
                await self._update_existing_license(existing_license, uuid, payload)
            else:
                await self._create_new_license(uuid, payload)

        except UnAuthorizedError as e:
            raise e
        except Exception as e:
            raise e

    async def _update_existing_license(
        self, existing_license, uuid: str, payload: UpdateUserPayload
    ):
        if existing_license.user_id != uuid:
            raise UnAuthorizedError(messages.LICENSE_IN_USE)
        else:
            payload.license.expiration_date = parse_date(
                payload.license.expiration_date
            )
            await self.driver_license_repository.update_by_uuid(
                uuid=existing_license.uuid, schema=payload.license
            )

    async def _create_new_license(self, uuid: str, payload: UpdateUserPayload):
        new_license_data = DriversLicenseFull(
            license_number=payload.license.license_number,
            front_url=payload.license.front_url,
            back_url=payload.license.back_url,
            expiration_date=parse_date(payload.license.expiration_date),
            user_id=uuid,
        )
        await self.driver_license_repository.create(new_license_data)

    async def patch_user_by_uuid(self, uuid: str, payload: UserProfileUdatePayload):
        try:
            # check uuid is valid
            if not UUID(uuid):
                return None
            user = await self.user_repository.patch_user_by_uuid(uuid, payload)
            return user if user else None
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    async def get_user_by_email_address(self, email: EmailStr):
        try:
            user = await self.user_repository.get_user_by_email_address(email)
            return user if user else None
        except Exception as e:
            raise e

    async def get_user_by_uuid(self, user_uuid: str):
        try:
            user = await self.user_repository.get_user_by_uuid(user_uuid)

            if not user:
                return None

            # Get the user's subscription plan
            # user_plan = await self.user_subscription_repository.get_user_subscription(
            #     user.get("email_address")
            # )

            # Default user package
            # user_package = []

            # # Check if the user has a valid subscription plan
            # if user_plan and user_plan.subscription_code:
            #     paystack_subscription = (
            #         await self.subscription_repository.get_paystack_subscription(
            #             user_plan.subscription_code
            #         )
            #     )
            #     user_package = {
            #         "package_name": paystack_subscription["plan"]["name"],
            #         "package_items": paystack_subscription["package_items"],
            #     }

            user["package"] = ""
            return user

        except Exception as e:
            # Log the exception or add custom error handling
            logging.error(f"An error occurred: {e}")
            raise e

    async def check_business_exists(self, name: str, email: str, phone: str):
        try:
            business = await self.user_repository.check_business_exists(
                name, email, phone
            )
            return business
        except Exception as e:
            raise e

    async def update_user_status(self, uuid: str):
        try:
            user = await self.user_repository.update_user_status(uuid)
            return user if user else None
        except Exception as e:
            raise e

    async def change_password(
        self,
        user_uuid: str,
        new_password: str,
    ):
        try:
            return await self.user_repository.change_password(user_uuid, new_password)
        except Exception as e:
            raise e

    async def update_user_avatar(self, user_id: str, avatar_url: str):
        try:
            return await self.user_repository.update_user_avatar(user_id, avatar_url)
        except Exception as e:
            raise e

    async def create_team_member_invitation(
        self,
        uuid: str,
        payload: InvitationCreatePayloadSingle,
        user: User,
        request: Request,
    ):
        try:
            if not user.business_profile_uuid:
                raise NotFoundError(
                    detail=messages.BUSINESS_PROFILE_NOT_FOUND + str(uuid)
                )
            invitations = await self.invitation_repository.create_invitation(
                payload=InvitationPayload(
                    business_profile_uuid=str(user.business_profile_uuid),
                    email=payload.email,
                    role_uuid=payload.role_uuid,
                    status=InvitationStatus.PENDING,
                    expired_at=datetime.now() + timedelta(days=3),
                )
            )

            return invitations
        except Exception as e:
            raise e

    async def create_admin_user_invitation(
        self, payload: InvitationCreatePayloadSingle, user: User, request: Request
    ):
        try:
            payload = AdminInvitationPayload(
                email=payload.email,
                role_uuid=payload.role_uuid,
                status=InvitationStatus.PENDING,
                expired_at=datetime.now() + timedelta(days=3),
                invitation_type=RoleType.ADMIN,
            )
            invite = await self.invitation_repository.create(payload)

            return invite
        except Exception as e:
            raise e

    async def deactivate_user_account(
        self,
        uuid: str,
        payload: AccountDeactivationPayload,
        user: User,
        request: Request,
    ):
        try:
            user = await self.user_repository.deactivate_account(uuid, payload)
            return user if user else None
        except Exception as e:
            raise e

    async def get_user_by_phone_number(self, phone_number: str):
        try:
            return await self.user_repository.get_user_by_phone_number(phone_number)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    async def get_all_admin_team_members(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        status=None,
    ):
        return await self.user_repository.get_admin_team_members(
            page, page_size, email, role_uuid, status
        )

    async def get_admin_team_member(self, team_member_uuid: str):
        try:
            return await self.user_repository.get_admin_team_member(team_member_uuid)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    async def get_all_accounts(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        start_date: str = None,
        end_date: str = None,
        status=None,
    ):
        return await self.user_repository.get_all_accounts(
            page, page_size, email, role_uuid, start_date, end_date, status
        )

    async def get_drivers_by_business_uuid(
        self,
        business_uuid,
        role_uuid,
        page,
        page_size,
        operator_type: List[str] = None,
        status: str = None,
        search: Optional[str] = None,
    ):
        return await self.user_repository.get_drivers_by_business_uuid(
            business_uuid,
            role_uuid,
            page,
            page_size,
            operator_type=operator_type,
            status=status,
            search=search,
        )

    async def get_driver_by_uuid(self, driver_uuid: str):
        driver = await self.user_repository.get_driver_by_uuid(driver_uuid=driver_uuid)
        if driver is None:
            raise NotFoundError(messages.USER_NOT_FOUND + driver_uuid)
        return driver

    async def update_team_member_handler(
        self,
        team_member_uuid: str,
        payload: UpdateAdminTeamMemberPayload,
        current_user: User,
        request: Request,
    ):
        try:
            await self.patch_by_uuid(team_member_uuid, payload)

            await self.user_repository.read_by_uuid(team_member_uuid)

            await self.role_repository.get_role(payload.user_role_uuid)

        except Exception as e:
            raise e

    async def get_user_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str,
        user_provided_dates: bool,
    ):
        current_data = await self.user_repository.get_user_stats(
            start_date, end_date, group_by
        )

        total_signups = sum(item["SignUps"] for item in current_data)
        total_converted = sum(item["Converted"] for item in current_data)
        total_unconverted = sum(item["Unconverted"] for item in current_data)

        signups_percentage_change = None
        converted_percentage_change = None
        unconverted_percentage_change = None

        if user_provided_dates:
            delta = end_date - start_date

            previous_start_date = start_date - delta
            previous_end_date = start_date - timedelta(days=1)

            previous_data = await self.user_repository.get_user_stats(
                previous_start_date, previous_end_date, group_by
            )

            prev_total_signups = sum(item["SignUps"] for item in previous_data)
            prev_total_converted = sum(item["Converted"] for item in previous_data)
            prev_total_unconverted = sum(item["Unconverted"] for item in previous_data)

            signups_percentage_change = calculate_percentage_change(
                total_signups, prev_total_signups
            )
            converted_percentage_change = calculate_percentage_change(
                total_converted, prev_total_converted
            )
            unconverted_percentage_change = calculate_percentage_change(
                total_unconverted, prev_total_unconverted
            )
        else:
            if len(current_data) >= 2:
                last_period = current_data[-1]
                prev_period = current_data[-2]

                signups_percentage_change = calculate_percentage_change(
                    last_period["SignUps"], prev_period["SignUps"]
                )
                converted_percentage_change = calculate_percentage_change(
                    last_period["Converted"], prev_period["Converted"]
                )
                unconverted_percentage_change = calculate_percentage_change(
                    last_period["Unconverted"], prev_period["Unconverted"]
                )
            else:
                signups_percentage_change = 0
                converted_percentage_change = 0
                unconverted_percentage_change = 0

        summary = {
            "total_signUps": total_signups,
            "total_converted": total_converted,
            "total_unconverted": total_unconverted,
            "total_signup_percentage_change": signups_percentage_change,
            "total_converted_percentage_change": converted_percentage_change,
            "total_unconverted_percentage_change": unconverted_percentage_change,
        }

        return {"data": current_data, "summary": summary}

    async def get_total_users(
        self, start_date: datetime, end_date: datetime, group_by: str
    ):
        return await self.user_repository.get_total_users(
            start_date, end_date, group_by
        )
