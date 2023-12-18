from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable

import structlog
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.security import hash_user_password
from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.email_verification import EmailVerification
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.auth_schema import EmailVerification as EmailVerficationSchema
from app.schema.auth_schema import UserEmailVerification
from app.schema.user_schema import IndividualUser, UpdateUserPayload, UserPayload
from app.util.enums import AccountType

log = structlog.get_logger()


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
                if user_to_update is None:
                    raise NotFoundError(detail=uuid)

                return self.update_by_uuid(uuid, user)
        except Exception as e:
            raise e

    def get_user_by_email_address(self, email: EmailStr) -> User:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.email_address == email)
                .first()
            )

    def get_user_by_phone_number(self, phone_number: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.phone_number == phone_number)
                .first()
            )

    def create_user(self, user: UserPayload):
        with self.session_factory() as session:
            db_user = self.model(
                first_name=user.first_name,
                last_name=user.last_name,
                location=user.location,
                address=user.address,
                phone_number=user.phone_number,
                email_address=user.email_address,
                password=hash_user_password(user.password),
                account_type=user.account_type,
                role=user.role,
            )

            session.add(db_user)
            session.commit()
            created_user = (
                session.query(self.model)
                .filter(self.model.email_address == db_user.email_address)
                .first()
            )

            returned_user = IndividualUser(**created_user.__dict__)

            if user.account_type == AccountType.BUSINESS:
                business_data = BusinessProfile(
                    business_name=user.business_name,
                    business_email=user.business_email,
                    business_phone=user.business_phone,
                )

                session.add(business_data)
                session.commit()

                returned_user = {
                    "first_name": created_user.first_name,
                    "last_name": created_user.last_name,
                    "location": created_user.location,
                    "address": created_user.address,
                    "phone_number": created_user.phone_number,
                    "email_address": created_user.email_address,
                    "uuid": created_user.uuid,
                    "account_type": created_user.account_type,
                    "business_name": user.business_name,
                    "business_email": user.business_email,
                    "business_phone": user.business_phone,
                    "role": created_user.role,
                }

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
