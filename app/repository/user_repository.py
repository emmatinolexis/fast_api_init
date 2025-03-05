import uuid
from datetime import datetime, timedelta
from typing import Callable, List, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from pydantic import EmailStr
from sqlalchemy import delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.security import extract_user_data, hash_user_password
from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.email_verification import EmailVerification
from app.model.invitation import Invitation
from app.model.role import Role
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.schema.auth_schema import EmailVerification as EmailVerficationSchema
from app.schema.auth_schema import UserEmailVerification
from app.schema.user_schema import (
    AccountDeactivationPayload,
    UpdateUserPayload,
    UserPayload,
    UserProfileUdatePayload,
)
from app.util.enums import (
    AccountType,
    ActiveStatus,
    CustomerRoles,
    InvitationStatus,
    RoleType,
)
from app.util.utils import calculate_percentage_change, datetime_parser, toggle_status


class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, User)

    async def update_user_by_uuid(self, uuid: str, user: UpdateUserPayload):
        """Updates a user by UUID asynchronously."""
        async with self.session_factory() as session:
            # Query user by UUID (since session.get() requires full primary key)
            result = await session.execute(select(User).filter(User.uuid == uuid))
            user_to_update = result.scalars().first()

            if user_to_update is None:
                raise Exception("User not found")

            # Update fields
            user_to_update.location = user.location
            user_to_update.address = user.address
            user_to_update.phone_number = user.phone_number
            user_to_update.country = user.country

            if user.phone_number is not None:
                user_to_update.operator_type = user.operator_type

            if user_to_update.onboarding_status is None:
                user_to_update.onboarding_status = datetime.now().isoformat()

            await session.commit()
            await session.refresh(user_to_update)

    async def get_user_by_email_address(self, email: EmailStr):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .filter(self.model.email_address == email)
                .options(joinedload(User.business_profile))
                .options(joinedload(User.user_role).joinedload(Role.permissions))
                .options(joinedload(User.driver_license))
            )
            return result.unique().scalar_one_or_none()

    async def get_user_by_phone_number(self, phone_number: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User)
                .filter(User.phone_number == phone_number)
                .options(joinedload(User.business_profile))
                .options(joinedload(User.driver_license))
                .options(joinedload(User.user_role).joinedload(Role.permissions))
            )
            user = result.unique().scalar_one_or_none()

            if not user:
                return None

            user_data = extract_user_data(user)
            return user_data

    async def update_user_status(self, uuid: str):
        """Toggle a user's status asynchronously."""
        async with self.session_factory() as session:
            # Query the user using select + filter instead of session.get()
            result = await session.execute(
                select(self.model).filter(self.model.uuid == uuid)
            )
            user = result.scalars().first()

            if user is None:
                raise Exception("User not found")

            # Toggle the status
            user.status = toggle_status(user.status)

            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_by_uuid(self, user_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User)
                .filter(User.uuid == user_uuid)
                .options(
                    selectinload(User.business_profile),
                    selectinload(User.driver_license),
                    selectinload(User.user_role).selectinload(Role.permissions),
                )
            )
            user: Optional[User] = result.scalars().unique().first()

            # return user
            if not user:
                return None
            user_data = extract_user_data(user)
            return user_data

    async def check_business_exists(self, name, email, phone):
        async with self.session_factory() as session:
            result = await session.execute(
                select(BusinessProfile).filter(
                    (BusinessProfile.business_name == name)
                    | (BusinessProfile.business_email == email)
                    | (BusinessProfile.business_phone == phone)
                )
            )
            business_data = result.scalar_one_or_none()
            return business_data

    async def change_password(self, user_uuid: str, new_password: str):
        """Changes a user's password asynchronously."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == user_uuid)
            )
            user = result.scalars().first()
            if not user:
                return None  # Return None if user is not found

            # Hash and update the password
            user.password = hash_user_password(new_password)

            await session.commit()
            await session.refresh(user)
            return True
            # return extract_user_data(user)

    async def update_user_onboard_status(self, uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == uuid)
            )
            user = result.scalar_one_or_none()
            user.onboarding_status = datetime.now()
            await session.commit()
            await session.refresh(user)
            return extract_user_data(user)

    async def get_account_users(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        search: str = None,
        role_uuids: list[str] = None,
        status: InvitationStatus = None,
        exclude_user_uuid: str = None,
    ):
        async with self.session_factory() as session:
            query = select(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            if exclude_user_uuid:
                query = query.filter(self.model.uuid != exclude_user_uuid)

            if search:
                search = f"%{search.strip().lower()}%"
                search_filter = or_(
                    self.model.first_name.ilike(search),
                    self.model.last_name.ilike(search),
                    self.model.email_address.ilike(search),
                )
                query = query.filter(search_filter)

            if role_uuids:
                valid_role_uuids = []
                for role_uuid in role_uuids:
                    try:
                        valid_role_uuids.append(UUID(role_uuid))
                    except ValueError:
                        continue
                if valid_role_uuids:
                    query = query.filter(
                        self.model.user_role_uuid.in_(valid_role_uuids)
                    )

            if status:
                query = query.filter(self.model.status == status)

            total_users = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            total_pages = (total_users + page_size - 1) // page_size

            offset = (page - 1) * page_size
            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            results = await session.execute(query.options(joinedload(User.user_role)))
            account_users = results.unique().scalars().all()

            users_data = [
                {
                    "uuid": user.uuid,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email_address": user.email_address,
                    "phone_number": user.phone_number,
                    "image_url": user.avatar_url,
                    "status": user.status,
                    "role": user.user_role,
                    "created_at": user.created_at,
                }
                for user in account_users
            ]

            return {
                "users": users_data,
                "total_users": total_users,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_admin_team_members(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        status=None,
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size
            # Build the query for invitations with optional filters
            query = select(self.model).filter(self.model.role == RoleType.ADMIN)

            # Add filters based on provided parameters
            if email:
                query = query.filter(self.model.email_address.ilike(f"%{email}%"))
            if role_uuid:
                query = query.filter(self.model.user_role_uuid == role_uuid)
            if status:
                query = query.filter(self.model.status == ActiveStatus(status))
            # Query to get the total count of invitations with filters
            total_team_members = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )

            # Calculate total pages
            total_pages = (total_team_members + page_size - 1) // page_size

            # Get the invitations with filters, pagination, and sorting
            results = await session.execute(
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.user_role))
            )
            users = results.unique().scalars().all()

            # Prepare the invitation data
            users_data = [
                {
                    "uuid": user.uuid,
                    "email": user.email_address,
                    "role": user.user_role,
                    "status": user.status,
                    "created_at": user.created_at,
                    "name": f"{user.first_name} {user.last_name}",
                    "phone_number": user.phone_number,
                    "profile_picture_url": user.avatar_url,
                }
                for user in users
            ]

            return {
                "team_members": users_data,
                "total_team_members": total_team_members,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def apply_filters(
        self,
        query,
        email: str = None,
        role_uuid: str = None,
        start_date_obj=None,
        end_date_obj=None,
        status=None,
    ):
        """Applies optional filters to the query."""
        if email:
            query = query.filter(self.model.email_address.ilike(f"%{email}%"))
        if role_uuid:
            query = query.filter(self.model.user_role_uuid == role_uuid)
        if start_date_obj:
            query = query.filter(self.model.created_at >= start_date_obj)
        if end_date_obj:
            query = query.filter(self.model.created_at <= end_date_obj)
        if status:
            query = query.filter(self.model.status == ActiveStatus(status))
        return query

    async def get_total_businesses(
        self, session, start_date_obj=None, end_date_obj=None
    ):
        """Fetches the count of businesses within the date range, if provided."""
        business_query = select(func.count()).select_from(BusinessProfile)

        if start_date_obj and end_date_obj:
            business_query = business_query.filter(
                BusinessProfile.created_at.between(start_date_obj, end_date_obj)
            )

        return await session.scalar(business_query)

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
        async with self.session_factory() as session:
            # Calculate offset for pagination
            offset = (page - 1) * page_size

            # Initialize date variables
            start_date_obj = None
            end_date_obj = None
            previous_start_date_obj = None
            previous_end_date_obj = None

            # Parse start and end dates
            if start_date and end_date:
                start_date_obj = datetime_parser(start_date)
                end_date_obj = datetime_parser(end_date)
                previous_end_date_obj = start_date_obj - timedelta(days=1)
                previous_start_date_obj = previous_end_date_obj - (
                    end_date_obj - start_date_obj
                )

            # Build the base query with filters
            query = select(self.model).filter(self.model.role != RoleType.ADMIN)
            query = await self.apply_filters(
                query, email, role_uuid, start_date_obj, end_date_obj, status
            )

            # Total records in date range
            total_records = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            total_active_users = await session.scalar(
                select(func.count()).select_from(
                    query.filter(self.model.status == ActiveStatus.ACTIVE).subquery()
                )
            )
            total_inactive_users = await session.scalar(
                select(func.count()).select_from(
                    query.filter(self.model.status == ActiveStatus.INACTIVE).subquery()
                )
            )
            total_organizations = await self.get_total_businesses(session)

            # Previous period data
            previous_query = select(self.model).filter(
                self.model.role != RoleType.ADMIN
            )
            previous_query = await self.apply_filters(
                previous_query,
                email,
                role_uuid,
                previous_start_date_obj,
                previous_end_date_obj,
                status,
            )
            previous_total_records = await session.scalar(
                select(func.count()).select_from(previous_query.subquery())
            )
            previous_active_users = await session.scalar(
                select(func.count()).select_from(
                    previous_query.filter(
                        self.model.status == ActiveStatus.ACTIVE
                    ).subquery()
                )
            )
            previous_inactive_users = await session.scalar(
                select(func.count()).select_from(
                    previous_query.filter(
                        self.model.status == ActiveStatus.INACTIVE
                    ).subquery()
                )
            )
            previous_organizations_query = select(func.count()).select_from(
                BusinessProfile
            )
            if start_date_obj is not None:
                previous_organizations_query = previous_organizations_query.filter(
                    BusinessProfile.created_at < start_date_obj
                )
            previous_organizations = await session.scalar(previous_organizations_query)

            # Calculate total pages
            total_pages = (total_records + page_size - 1) // page_size

            # Fetch users with pagination and eager loading
            results = await session.execute(
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.business_profile))
                .options(joinedload(self.model.user_role))
            )
            users = results.unique().scalars().all()

            # Prepare the user data for output
            users_data = [
                {
                    "email": user.email_address,
                    "role": user.user_role.role_name if user.user_role else None,
                    "status": user.status,
                    "registered_on": user.created_at,
                    "name": f"{user.first_name} {user.last_name}",
                    "business_name": (
                        user.business_profile.business_name
                        if user.business_profile
                        else None
                    ),
                }
                for user in users
            ]

            # Calculate percentage changes
            percentage_change_total = calculate_percentage_change(
                total_records, previous_total_records
            )
            percentage_change_active = calculate_percentage_change(
                total_active_users, previous_active_users
            )
            percentage_change_inactive = calculate_percentage_change(
                total_inactive_users, previous_inactive_users
            )
            percentage_change_total_organizations = calculate_percentage_change(
                total_organizations, previous_organizations
            )

            # Return the result in the desired format
            return {
                "users": users_data,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "summary": {
                    "total_accounts": total_records,
                    "active_accounts": total_active_users,
                    "inactive_accounts": total_inactive_users,
                    "total_organizations": total_organizations,
                    "previous_summary": {
                        "total_accounts": previous_total_records,
                        "active_accounts": previous_active_users,
                        "inactive_accounts": previous_inactive_users,
                        "total_organizations": previous_organizations,
                    },
                    "percentage_change": {
                        "total_accounts": percentage_change_total,
                        "active_accounts": percentage_change_active,
                        "inactive_accounts": percentage_change_inactive,
                        "total_organizations": percentage_change_total_organizations,
                    },
                },
            }

    async def get_admin_team_member(self, team_member_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .filter(self.model.uuid == team_member_uuid)
                .options(joinedload(User.user_role))
            )

            user = result.unique().scalar_one_or_none()

            if not user:
                return None

            user_data = {
                "uuid": user.uuid,
                "email": user.email_address,
                "role": user.user_role,
                "status": user.status,
                "created_at": user.created_at,
                "name": f"{user.first_name} {user.last_name}",
                "phone_number": user.phone_number,
                "profile_picture_url": user.avatar_url,
            }

            return user_data

    async def create_user(self, user: UserPayload):
        async with self.session_factory() as session:
            try:
                db_user = await self._create_user_entry(session, user)
                await self._handle_invitation_status(session, user)

                if (
                    user.account_type == AccountType.BUSINESS
                    or user.account_type == AccountType.INDIVIDUAL
                ) and not user.invite_status:
                    returned_user = await self._handle_business_account(
                        session, user, db_user
                    )
                else:
                    returned_user = await self._build_user_response(session, db_user)

                await session.commit()
                return returned_user
            except Exception as e:
                raise e

    async def _create_user_entry(self, session, user: UserPayload):
        db_user = self.model(
            first_name=user.first_name,
            last_name=user.last_name,
            email_address=user.email_address,
            password=hash_user_password(user.password),
            account_type=user.account_type,
            role=user.role,
            business_profile_uuid=(
                user.business_profile_uuid if user.invite_status else None
            ),
            user_role_uuid=(
                CustomerRoles.ADMIN.value
                if not user.invite_status
                else user.user_role_uuid
            ),
            status=user.status,
            verifiedAt=(
                f"{datetime.utcnow():%Y-%m-%d %H:%M:%S%z}"
                if user.invite_status
                else None
            ),
        )

        session.add(db_user)
        await session.commit()
        return db_user

    async def _handle_invitation_status(self, session, user: UserPayload):
        if user.invite_status:
            # Delete the invitation where the email matches
            await session.execute(
                delete(Invitation).where(Invitation.email == user.email_address)
            )
            await session.commit()

    async def _handle_business_account(self, session, user: UserPayload, db_user):
        if db_user.account_type == AccountType.BUSINESS:
            business_data = BusinessProfile(
                business_name=user.business_name,
                business_email=user.business_email,
                business_phone=user.business_phone,
            )

        # generate dummy business if account type is individual
        if db_user.account_type == AccountType.INDIVIDUAL:
            business_data = BusinessProfile(
                business_name=f"{db_user.first_name}_{db_user.last_name}_{uuid.uuid4().hex[:8]}",
                business_email=f"{db_user.email_address}",
                business_phone=f"{db_user.phone_number}_{db_user.last_name}_{uuid.uuid4().hex[:8]}",
            )

        session.add(business_data)
        await session.commit()
        await session.refresh(business_data)

        # Update user with business profile
        result = await session.execute(
            select(self.model).filter(self.model.email_address == db_user.email_address)
        )
        created_user = result.scalar_one_or_none()
        created_user.business_profile_uuid = business_data.uuid
        await session.commit()
        await session.refresh(created_user)

        return {
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "location": db_user.location,
            "address": db_user.address,
            "phone_number": db_user.phone_number,
            "email_address": db_user.email_address,
            "uuid": created_user.uuid,
            "status": created_user.status,
            "account_type": db_user.account_type,
            "business_name": user.business_name,
            "business_email": user.business_email,
            "business_phone": user.business_phone,
        }

    async def _build_user_response(self, session, db_user):
        result = await session.execute(
            select(self.model).filter(self.model.email_address == db_user.email_address)
        )
        created_user = result.scalar_one_or_none()
        return {
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "email_address": db_user.email_address,
            "uuid": created_user.uuid,
            "account_type": db_user.account_type,
            "status": created_user.status,
        }

    async def create_verification_token(
        self,
        user_verify: UserEmailVerification,
        verification_token: EmailVerficationSchema,
    ):
        async with self.session_factory() as session:
            current_date = datetime.now()

            from datetime import timedelta

            db_verify = EmailVerification(
                user_uuid=user_verify.uuid,
                verification_token=verification_token["verification_token"],
                expiry_date=(
                    current_date + timedelta(days=settings.VERIFY_TOKEN_EXPIRE_DAYS)
                ).isoformat(),
            )

            session.add(db_verify)
            await session.commit()

            result = await session.execute(
                select(self.model).filter(self.model.uuid == user_verify.uuid)
            )
            db_user = result.scalar_one_or_none()
            return db_user, verification_token["verification_token"]

    async def update_user_avatar(self, user_id: str, avatar_url: str) -> User:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == user_id)
            )
            user = result.scalar_one_or_none()
            user.avatar_url = avatar_url
            await session.commit()
            await session.refresh(user)
            return user

    async def deactivate_account(
        self, uuid: str, payload: AccountDeactivationPayload
    ) -> User:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == uuid)
            )
            user = result.scalar_one_or_none()
            user.status = ActiveStatus.DEACTIVATED
            user.deactivation_reason = payload.reason
            await session.commit()
            await session.refresh(user)
            return user

    async def patch_user_by_uuid(self, uuid: str, user: UserProfileUdatePayload):
        """Patch (partially update) a user profile by UUID asynchronously."""
        async with self.session_factory() as session:
            # Query the user using filter instead of session.get()
            result = await session.execute(
                select(self.model).filter(self.model.uuid == uuid)
            )
            user_to_update = result.scalars().first()

            if user_to_update is None:
                raise Exception("User not found")

            # Apply updates only if values are provided
            if user.first_name is not None:
                user_to_update.first_name = user.first_name
            if user.last_name is not None:
                user_to_update.last_name = user.last_name
            if user.location is not None:
                user_to_update.location = user.location

            await session.commit()
            await session.refresh(user_to_update)

            return user_to_update

    async def get_drivers_by_business_uuid(
        self,
        business_uuid,
        role_uuid,
        page=1,
        page_size=10,
        operator_type: List[str] = None,
        status: str = None,
        search: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            query = select(self.model).filter(
                User.business_profile_uuid == business_uuid,
                User.user_role_uuid == role_uuid,
            )

            if search:
                search_pattern = f"%{search.strip().lower()}%"
                query = query.filter(
                    or_(
                        func.lower(User.first_name).ilike(search_pattern),
                        func.lower(User.last_name).ilike(search_pattern),
                    )
                )

            if operator_type:
                query = query.filter(
                    func.upper(User.operator_type).in_(
                        [op.upper() for op in operator_type]
                    )
                )

            if status:
                query = query.filter(User.status == status)

            query = query.order_by(desc(User.created_at))

            total_drivers = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            total_pages = (total_drivers + page_size - 1) // page_size

            offset = (page - 1) * page_size
            drivers = (
                (await session.execute(query.offset(offset).limit(page_size)))
                .scalars()
                .all()
            )

            drivers_data = [
                {
                    "uuid": driver.uuid,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "email_address": driver.email_address,
                    "phone_number": driver.phone_number,
                    "license_url": driver.license_url,
                    "profile_picture": driver.avatar_url,
                    "operator_type": driver.operator_type,
                    "status": driver.status,
                    "created_at": driver.created_at,
                }
                for driver in drivers
            ]

            return {
                "drivers": drivers_data,
                "total_drivers": total_drivers,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_driver_by_uuid(self, driver_uuid: str):
        async with self.session_factory() as session:
            driver = await session.get(self.model, driver_uuid)

            if not driver:
                return None

            driver_data = {
                "uuid": driver.uuid,
                "first_name": driver.first_name,
                "last_name": driver.last_name,
                "email_address": driver.email_address,
                "phone_number": driver.phone_number,
                "license_url": driver.license_url,
                "profile_picture": driver.avatar_url,
                "operator_type": driver.operator_type,
                "status": driver.status,
                "created_at": driver.created_at,
            }

            return driver_data

    async def get_user_by_assigned_asset_uuid(self, assigned_asset_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).filter(User.assigned_asset_uuid == assigned_asset_uuid)
            )
            user = result.scalar_one_or_none()
            if user is None:
                return None

            return user

    async def get_user_stats(
        self, start_date: datetime, end_date: datetime, group_by: str = "month"
    ):
        async with self.session_factory() as session:
            data = {}
            periods = []

            if group_by == "month":
                current_period = datetime(start_date.year, start_date.month, 1)
                end_period = datetime(end_date.year, end_date.month, 1)
                while current_period <= end_period:
                    key = current_period.strftime("%b %y")
                    periods.append((current_period, key))
                    data[key] = {"Month": key, "SignUps": 0, "Converted": 0}
                    current_period += relativedelta(months=1)

                trunc_field = "month"
                key_format = "%b %y"

            elif group_by == "day":
                current_period = start_date
                while current_period <= end_date:
                    key = current_period.strftime("%Y-%m-%d")
                    periods.append((current_period, key))
                    data[key] = {"Date": key, "SignUps": 0, "Converted": 0}
                    current_period += timedelta(days=1)

                trunc_field = "day"
                key_format = "%Y-%m-%d"

            user_counts = (
                await session.execute(
                    select(
                        func.date_trunc(trunc_field, User.created_at).label("period"),
                        func.count(User.uuid).label("signups"),
                    )
                    .filter(User.created_at >= start_date, User.created_at <= end_date)
                    .group_by("period")
                    .order_by("period")
                )
            ).all()

            for period, signups in user_counts:
                key = period.strftime(key_format)
                if key in data:
                    data[key]["SignUps"] = signups

            conversion_counts = (
                await session.execute(
                    select(
                        func.date_trunc(trunc_field, UserSubscription.created_at).label(
                            "period"
                        ),
                        func.count(UserSubscription.uuid).label("conversions"),
                    )
                    .filter(
                        UserSubscription.created_at >= start_date,
                        UserSubscription.created_at <= end_date,
                    )
                    .group_by("period")
                    .order_by("period")
                )
            ).all()

            for period, conversions in conversion_counts:
                key = period.strftime(key_format)
                if key in data:
                    data[key]["Converted"] = conversions

            for item in data.values():
                item["Unconverted"] = item["SignUps"] - item["Converted"]

            sorted_data = [data[key] for _, key in sorted(periods)]

            return sorted_data

    async def get_total_users(
        self, start_date: datetime, end_date: datetime, group_by: str = "month"
    ):
        async with self.session_factory() as session:
            data = []
            total_users = await session.scalar(
                select(func.count(User.uuid)).filter(User.created_at <= end_date)
            )

            if group_by == "month":
                trunc_field = "month"
                date_format = "%b %y"
            elif group_by == "day":
                trunc_field = "day"
                date_format = "%Y-%m-%d"
            else:
                trunc_field = "month"
                date_format = "%b %y"

            user_counts = (
                await session.execute(
                    select(
                        func.date_trunc(trunc_field, User.created_at).label("period"),
                        func.count(User.uuid).label("count"),
                    )
                    .filter(User.created_at >= start_date, User.created_at <= end_date)
                    .group_by("period")
                    .order_by("period")
                )
            ).all()

            period_counts = {}
            for period, count in user_counts:
                period_key = period.strftime(date_format)
                period_counts[period_key] = count

            periods = []
            if group_by == "month":
                current_period = datetime(start_date.year, start_date.month, 1)
                end_period = datetime(end_date.year, end_date.month, 1)
                while current_period <= end_period:
                    periods.append(current_period)
                    current_period += relativedelta(months=1)
            elif group_by == "day":
                current_period = start_date
                while current_period <= end_date:
                    periods.append(current_period)
                    current_period += timedelta(days=1)

            cumulative_total = 0
            for period in periods:
                period_key = period.strftime(date_format)
                count = period_counts.get(period_key, 0)
                cumulative_total += count
                data.append({"date": period_key, "User": cumulative_total})

            return {"data": data, "total_users": total_users}
