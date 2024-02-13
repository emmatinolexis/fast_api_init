from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable

from pydantic import EmailStr
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_user_password, verify_password
from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.email_verification import EmailVerification
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.auth_schema import EmailVerification as EmailVerficationSchema
from app.schema.auth_schema import UserEmailVerification
from app.schema.user_schema import UpdateUserPayload, UserPayload, AccountDeactivationPayload
from app.util.enums import AccountType, ActiveStatus
from app.schema.user_schema import UpdateUserPayload, UserPayload, UpdateUserAvatar
from app.util.enums import AccountType
from app.util.utils import toggle_status


class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, User)

    def update_user_by_uuid(self, uuid: str, user: UpdateUserPayload):
        try:
            with self.session_factory() as session:
                user_to_update = (
                    session.query(self.model).filter(self.model.uuid == uuid).first()
                )
                if user is None:
                    raise Exception("User not found")

                # return self.update_by_uuid(uuid, user)
                user_to_update.location = user.location
                user_to_update.address = user.address
                user_to_update.phone_number = user.phone_number

                # Commit the changes to the database
                session.commit()
                session.refresh(user_to_update)

                return user_to_update
        except Exception as e:
            raise e

    def get_user_by_email_address(self, email: EmailStr) -> User:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.email_address == email)
                .options(joinedload(User.business_profile))
                .first()
            )

    def update_user_status(self, uuid: str) -> User:
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.status = toggle_status(user.status)
            session.commit()
            session.refresh(user)
            return user

    def get_user_by_phone_number(self, phone_number: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.phone_number == phone_number)
                .first()
            )

    def change_password(
        self,
        user_uuid: str,
        old_password: str,
        new_password: str,
        password_confirmation: str,
    ):
        with self.session_factory() as session:
            user = (
                session.query(self.model).filter(self.model.uuid == user_uuid).first()
            )

            # Check if the user exists
            if not user:
                raise Exception("User not found")

            # check if new password and confirm password match
            if not new_password == password_confirmation:
                raise Exception("New password and confirm password does not match")

            # Compare the old password with the stored hashed password
            if not verify_password(old_password, user.password):
                raise Exception("Incorrect old password provided")

            # Update the password with the new hashed password
            user.password = hash_user_password(new_password)

            # Commit the changes to the database
            session.commit()
            session.refresh(user)

            return user

    def update_user_onboard_status(self, uuid):
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.onboarding_status = datetime.now()
            session.commit()
            session.refresh(user)
            return user

    def create_user(self, user: UserPayload):
        with self.session_factory() as session:
            db_user = self.model(
                first_name=user.first_name,
                last_name=user.last_name,
                email_address=user.email_address,
                password=hash_user_password(user.password),
                account_type=user.account_type,
                role=user.role,
                status=user.status,
            )

            session.add(db_user)
            session.commit()
            created_user = (
                session.query(self.model)
                .filter(self.model.email_address == db_user.email_address)
                .first()
            )

            if user.account_type == AccountType.BUSINESS:
                try:
                    business_data = (
                        session.query(BusinessProfile)
                        .filter(
                            (BusinessProfile.business_name == user.business_name)
                            | (BusinessProfile.business_email == user.business_email)
                        )
                        .first()
                    )
                    if business_data is not None:
                        raise Exception("Business already exists")

                    business_data = BusinessProfile(
                        business_name=user.business_name,
                        business_email=user.business_email,
                        business_phone=user.business_phone,
                    )

                    session.add(business_data)

                    returned_user = {
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
                except Exception as e:
                    session.rollback()  # rollback user creation
                    raise e
            else:
                returned_user = {
                    "first_name": db_user.first_name,
                    "last_name": db_user.last_name,
                    "email_address": db_user.email_address,
                    "uuid": created_user.uuid,
                    "account_type": db_user.account_type,
                    "status": created_user.status,
                }
            session.commit()
            return returned_user

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

    def deactivate_account(self, uuid: str, payload: AccountDeactivationPayload) -> User:
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == uuid).first()
            user.status = ActiveStatus.DEACTIVATED
            user.deactivation_reason = payload.reason
            session.commit()
            session.refresh(user)
            return user

    def update_user_avatar(self, user_id: str, avatar_url: str) -> User:
        with self.session_factory() as session:
            user = session.query(self.model).filter(self.model.uuid == user_id).first()
            user.avatar_url = avatar_url
            session.commit()
            session.refresh(user)
            return user
