from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable, List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.security import extract_user_data, hash_user_password
from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.email_verification import EmailVerification
from app.model.invitation import Invitation
from app.model.role import Role
from app.model.user import User
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
from app.util.utils import parse_date, toggle_status,calculate_percentage_change,datetime_parser


class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, User)

    def update_user_by_uuid(self, uuid: str, user: UpdateUserPayload):
        try:
            with self.session_factory() as session:
                user_to_update = session.query(User).filter(User.uuid == uuid).first()
                if user_to_update is None:
                    raise Exception("User not found")

                user_to_update.location = user.location
                user_to_update.address = user.address
                user_to_update.phone_number = user.phone_number
                user_to_update.country = user.country

                if user.phone_number is not None:
                    user_to_update.operator_type = user.operator_type

                # set onboarding status
                if user_to_update.onboarding_status is None:
                    user_to_update.onboarding_status = datetime.now()

                # Commit the changes to the database
                session.commit()
                session.refresh(user_to_update)

                return
        except Exception as e:
            raise e

    def get_user_by_email_address(self, email: EmailStr):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.email_address == email)
                .options(joinedload(User.business_profile))
                .options(joinedload(User.user_role).joinedload(Role.permissions))
                .options(joinedload(User.driver_license))
                .first()
            )

    def get_user_by_phone_number(self, phone_number: str):
        with self.session_factory() as session:
            user = (
                session.query(User)
                .filter(User.phone_number == phone_number)
                .options(joinedload(User.business_profile))
                .options(joinedload(User.driver_license))
                .options(joinedload(User.user_role).joinedload(Role.permissions))
                .first()
            )

            if not user:
                return None

            user_data = extract_user_data(user)
            return user_data

    def update_user_status(self, uuid: str):
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.status = toggle_status(user.status)
            session.commit()
            session.refresh(user)
            return user

    def get_user_by_uuid(self, user_uuid: str):
        with self.session_factory() as session:
            # Query the user model with necessary joins
            user: Optional[User] = (
                session.query(self.model)
                .filter(User.uuid == user_uuid)
                .options(joinedload(User.business_profile))
                .options(joinedload(User.user_role).joinedload(Role.permissions))
                .first()
            )

            # If the user is not found, return None
            if not user:
                return None

            # Process and return user data if user exists
            user_data = extract_user_data(user)

            return user_data

    def check_business_exists(self, name, email, phone):
        with self.session_factory() as session:
            business_data = (
                session.query(BusinessProfile)
                .filter(
                    (BusinessProfile.business_name == name)
                    | (BusinessProfile.business_email == email)
                    | (BusinessProfile.business_phone == phone)
                )
                .first()
            )
            return business_data is not None

    def change_password(
        self,
        user_uuid,
        new_password: str,
    ):
        with self.session_factory() as session:
            user = (
                session.query(self.model).filter(self.model.uuid == user_uuid).first()
            )

            if not user:
                return None

            user.password = hash_user_password(new_password)
            session.commit()
            session.refresh(user)

            return extract_user_data(user)

    def update_user_onboard_status(self, uuid):
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.onboarding_status = datetime.now()
            session.commit()
            session.refresh(user)
            return extract_user_data(user)

    def get_account_users(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        search: str = None,
        role_uuids: list[str] = None,
        status: InvitationStatus = None,
    ):
        with self.session_factory() as session:
            query = session.query(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            # Apply filters
            if search:
                search = f"%{search.strip().lower()}%"
                search_filter = or_(
                    self.model.first_name.ilike(search),
                    self.model.last_name.ilike(search),
                    self.model.email_address.ilike(search),
                )
                query = query.filter(search_filter)

            if role_uuids:
                # Validate and convert role_uuids to proper UUID objects
                valid_role_uuids = []
                for role_uuid in role_uuids:
                    try:
                        valid_role_uuids.append(UUID(role_uuid))
                    except ValueError:
                        # Skip invalid UUIDs
                        continue
                if valid_role_uuids:
                    query = query.filter(
                        self.model.user_role_uuid.in_(valid_role_uuids)
                    )

            if status:
                query = query.filter(self.model.status == status)

            # Get total count and pages
            total_users = query.count()
            total_pages = (total_users + page_size - 1) // page_size

            # Apply pagination
            offset = (page - 1) * page_size
            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            # Fetch users with roles
            account_users = query.options(joinedload(User.user_role)).all()

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

    def get_admin_team_members(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        status=None,
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            # Build the query for invitations with optional filters
            query = session.query(self.model).filter(self.model.role == RoleType.ADMIN)

            # Add filters based on provided parameters
            if email:
                query = query.filter(self.model.email_address.ilike(f"%{email}%"))
            if role_uuid:
                query = query.filter(self.model.user_role_uuid == role_uuid)
            if status:
                query = query.filter(self.model.status == ActiveStatus(status))
            # Query to get the total count of invitations with filters
            total_team_members = query.with_entities(func.count(self.model.id)).scalar()

            # Calculate total pages
            total_pages = (total_team_members + page_size - 1) // page_size

            # Get the invitations with filters, pagination, and sorting
            users = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.user_role))
                .all()
            )

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

    def apply_filters(
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

    def get_total_businesses(self, session, start_date_obj=None, end_date_obj=None):
        """Fetches the count of businesses within the date range, if provided."""
        business_query = session.query(BusinessProfile)

        if start_date_obj and end_date_obj:
            business_query = business_query.filter(
                BusinessProfile.created_at.between(start_date_obj, end_date_obj)
            )

        return business_query.count()

    def get_all_accounts(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuid: str = None,
        start_date: str = None,
        end_date: str = None,
        status=None,
    ):
        with self.session_factory() as session:
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
                previous_start_date_obj = previous_end_date_obj - (end_date_obj - start_date_obj)

            # Build the base query with filters
            query = session.query(self.model).filter(self.model.role != RoleType.ADMIN)
            query = self.apply_filters(query, email, role_uuid, start_date_obj, end_date_obj, status)

            # Total records in date range
            total_records = query.with_entities(func.count(self.model.id)).scalar()
            total_active_users = query.filter(self.model.status == ActiveStatus.ACTIVE).count()
            total_inactive_users = query.filter(self.model.status == ActiveStatus.INACTIVE).count()
            total_organizations = session.query(BusinessProfile).count()

            # Previous period data
            previous_query = session.query(self.model).filter(self.model.role != RoleType.ADMIN)
            previous_query = self.apply_filters(previous_query, email, role_uuid, previous_start_date_obj, previous_end_date_obj, status)
            previous_total_records = previous_query.with_entities(func.count(self.model.id)).scalar()
            previous_active_users = previous_query.filter(self.model.status == ActiveStatus.ACTIVE).count()
            previous_inactive_users = previous_query.filter(self.model.status == ActiveStatus.INACTIVE).count()
            previous_organizations_query = session.query(BusinessProfile)
            if start_date_obj is not None:
                previous_organizations_query = previous_organizations_query.filter(BusinessProfile.created_at < start_date_obj)
            previous_organizations = previous_organizations_query.count()



            # Calculate total pages
            total_pages = (total_records + page_size - 1) // page_size

            # Fetch users with pagination and eager loading
            users = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.business_profile))
                .options(joinedload(self.model.user_role))
                .all()
            )

            # Prepare the user data for output
            users_data = [
                {
                    "email": user.email_address,
                    "role": user.user_role.role_name if user.user_role else None,
                    "status": user.status,
                    "registered_on": user.created_at,
                    "name": f"{user.first_name} {user.last_name}",
                    "business_name": user.business_profile.business_name if user.business_profile else None,
                }
                for user in users
            ]

            # Calculate percentage changes
            percentage_change_total = calculate_percentage_change(total_records, previous_total_records)
            percentage_change_active = calculate_percentage_change(total_active_users, previous_active_users)
            percentage_change_inactive = calculate_percentage_change(total_inactive_users, previous_inactive_users)
            percentage_change_total_organizations = calculate_percentage_change(total_organizations, previous_organizations)

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


    def get_admin_team_member(self, team_member_uuid: str):
        with self.session_factory() as session:
            user = (
                session.query(self.model)
                .filter(self.model.uuid == team_member_uuid)
                .options(joinedload(User.user_role))
                .first()
            )

            if not user:
                return None

            user = {
                "uuid": user.uuid,
                "email": user.email_address,
                "role": user.user_role,
                "status": user.status,
                "created_at": user.created_at,
                "name": f"{user.first_name} {user.last_name}",
                "phone_number": user.phone_number,
                "profile_picture_url": user.avatar_url,
            }

            return user

    def create_user(self, user: UserPayload):
        with self.session_factory() as session:
            try:
                db_user = self._create_user_entry(session, user)
                self._handle_invitation_status(session, user)

                if user.account_type == AccountType.BUSINESS and not user.invite_status:
                    returned_user = self._handle_business_account(
                        session, user, db_user
                    )
                else:
                    returned_user = self._build_user_response(session, db_user)

                session.commit()
                return returned_user
            except Exception as e:
                session.rollback()
                raise e

    def _create_user_entry(self, session, user: UserPayload):
        db_user = self.model(
            first_name=user.first_name,
            last_name=user.last_name,
            email_address=user.email_address,
            password=hash_user_password(user.password),
            account_type=user.account_type,
            role=user.role,
            business_profile_uuid=user.business_profile_uuid
            if user.invite_status
            else None,
            user_role_uuid=CustomerRoles.ADMIN
            if not user.invite_status
            else user.user_role_uuid,
            status=user.status,
            verifiedAt=datetime.utcnow() if user.invite_status else None,
        )

        session.add(db_user)
        session.commit()
        return db_user

    def _handle_invitation_status(self, session, user: UserPayload):
        if user.invite_status:
            # Delete the invitation where the email matches
            session.query(Invitation).filter(
                Invitation.email == user.email_address
            ).delete()
            session.commit()

    def _handle_business_account(self, session, user: UserPayload, db_user):
        business_data = BusinessProfile(
            business_name=user.business_name,
            business_email=user.business_email,
            business_phone=user.business_phone,
        )

        session.add(business_data)
        session.commit()
        session.refresh(business_data)

        # Update user with business profile
        created_user = (
            session.query(self.model)
            .filter(self.model.email_address == db_user.email_address)
            .first()
        )
        created_user.business_profile_uuid = business_data.uuid
        session.commit()
        session.refresh(created_user)

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

    def _build_user_response(self, session, db_user):
        created_user = (
            session.query(self.model)
            .filter(self.model.email_address == db_user.email_address)
            .first()
        )
        return {
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "email_address": db_user.email_address,
            "uuid": created_user.uuid,
            "account_type": db_user.account_type,
            "status": created_user.status,
        }

    def create_verification_token(
        self,
        user_verify: UserEmailVerification,
        verification_token: EmailVerficationSchema,
    ):
        with self.session_factory() as session:
            current_date = datetime.now()

            db_verify = EmailVerification(
                user_uuid=user_verify.uuid,
                verification_token=verification_token["verification_token"],
                expiry_date=current_date
                + timedelta(days=settings.VERIFY_TOKEN_EXPIRE_DAYS),
            )

            session.add(db_verify)
            session.commit()

            db_user = (
                session.query(self.model)
                .filter(self.model.uuid == user_verify.uuid)
                .first()
            )

            return db_user, verification_token["verification_token"]

    def update_user_avatar(self, user_id: str, avatar_url: str) -> User:
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == user_id).first()
            user.avatar_url = avatar_url
            session.commit()
            session.refresh(user)
            return user

    def deactivate_account(
        self, uuid: str, payload: AccountDeactivationPayload
    ) -> User:
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.status = ActiveStatus.DEACTIVATED
            user.deactivation_reason = payload.reason
            session.commit()
            session.refresh(user)
            return user

    def patch_user_by_uuid(self, uuid: str, user: UserProfileUdatePayload):
        try:
            with self.session_factory() as session:
                user_to_update = (
                    session.query(self.model).filter(self.model.uuid == uuid).first()
                )
                if user_to_update is None:
                    raise Exception("User not found")

                # return self.update_by_uuid(uuid, user)
                if user.first_name is not None:
                    user_to_update.first_name = user.first_name
                if user.last_name is not None:
                    user_to_update.last_name = user.last_name
                if user.location is not None:
                    user_to_update.location = user.location

                # Commit the changes to the database
                session.commit()
                session.refresh(user_to_update)

                return user_to_update
        except Exception as e:
            raise e

    def get_drivers_by_business_uuid(
        self,
        business_uuid,
        role_uuid,
        page=1,
        page_size=10,
        operator_type: List[str] = None,
        status: str = None,
    ):
        try:
            with self.session_factory() as session:
                # Build the query to filter drivers by business and role, and order by created_at descending
                query = session.query(self.model).filter(
                    User.business_profile_uuid == business_uuid,
                    User.user_role_uuid == role_uuid,
                )  # Order by created_at in descending order

                # Apply additional filters if provided
                if operator_type:
                    query = query.filter(User.operator_type.in_(operator_type))
                if status:
                    query = query.filter(User.status == status)

                query = query.order_by(
                    desc(User.created_at)
                )  # Order by created_at in descending order

                # Get total count of drivers
                total_drivers = query.count()

                # Calculate total pages
                total_pages = (total_drivers + page_size - 1) // page_size

                # Apply pagination
                offset = (page - 1) * page_size
                drivers = query.offset(offset).limit(page_size).all()

                # Prepare the driver data
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
        except Exception as e:
            raise e

    def get_driver_by_uuid(self, driver_uuid: str):
        try:
            with self.session_factory() as session:
                driver = (
                    session.query(self.model)
                    .filter(self.model.uuid == driver_uuid)
                    .first()
                )

                if not driver:
                    return None

                # Prepare the driver data for output
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
        except Exception as e:
            raise e

    def get_user_by_assigned_asset_uuid(self, assigned_asset_uuid: str):
        try:
            with self.session_factory() as session:
                # Query the User model to find the user with the given assigned_asset_uuid
                user = (
                    session.query(User)
                    .filter(User.assigned_asset_uuid == assigned_asset_uuid)
                    .first()
                )
                if user is None:
                    return None

                return user
        except Exception as e:
            raise e
