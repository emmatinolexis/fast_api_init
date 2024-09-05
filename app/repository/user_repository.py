from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable, Optional

from pydantic import EmailStr
from sqlalchemy import desc, func
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
from app.util.enums import AccountType, ActiveStatus, CustomerRoles, InvitationStatus
from app.util.utils import toggle_status


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

                # return self.update_by_uuid(uuid, user)
                user_to_update.location = user.location
                user_to_update.address = user.address
                user_to_update.phone_number = user.phone_number
                user_to_update.country = user.country

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
                .first()
            )

    def get_user_by_phone_number(self, phone_number: str):
        with self.session_factory() as session:
            user = (
                session.query(User)
                .filter(User.phone_number == phone_number)
                .options(joinedload(User.business_profile))
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
        user_uuid: str,
        new_password: str,
    ):
        with self.session_factory() as session:
            user = (
                session.query(User).filter(User.uuid == user_uuid).first()
            )

            user.password = hash_user_password(new_password)

            # Commit the changes to the database
            session.commit()
            session.refresh(user)

            return

    def update_user_onboard_status(self, uuid):
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.onboarding_status = datetime.now()
            session.commit()
            session.refresh(user)
            return extract_user_data(user)

    def get_account_users(self, business_uuid: str, page=1, page_size=10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of users
            total_users = (
                session.query(func.count(self.model.id))
                .filter(self.model.business_profile_uuid == business_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_users + page_size - 1) // page_size

            account_users = (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(User.user_role))
            )

            users_data = []
            for user in account_users:
                user_data = {
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
                users_data.append(user_data)

            return {
                "users": users_data,
                "total_users": total_users,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    # def get_account_users(self, business_uuid: str, page=1, page_size=10):
    #     with self.session_factory() as session:
    #         offset = (page - 1) * page_size
    #
    #         account_users = (
    #             session.query(self.model)
    #             .filter(self.model.business_profile_uuid == business_uuid)
    #             .order_by(desc(self.model.created_at)).offset(offset).limit(page_size)
    #             .options(joinedload(User.user_role))
    #         )
    #         users_data = []
    #         for user in account_users:
    #             user_data = {
    #                 "uuid": user.uuid,
    #                 "first_name": user.first_name,
    #                 "last_name": user.last_name,
    #                 "email_address": user.email_address,
    #                 "phone_number": user.phone_number,
    #                 "image_url": user.avatar_url,
    #                 "status": user.status,
    #                 "role": user.user_role,
    #                 "created_at": user.created_at,
    #             }
    #             users_data.append(user_data)
    #
    #         return users_data

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
        )

        session.add(db_user)
        session.commit()
        return db_user

    def _handle_invitation_status(self, session, user: UserPayload):
        if user.invite_status:
            invite = (
                session.query(Invitation)
                .filter(Invitation.email == user.email_address)
                .first()
            )
            if invite:
                invite.status = InvitationStatus.ACCEPTED
                session.commit()
                session.refresh(invite)

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
