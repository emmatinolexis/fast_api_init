from datetime import datetime

from fastapi import Request
from jose import jwt

from app.core import activity_log_constants
from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.core.exceptions import (
    AlreadyVerifiedError,
    AuthError,
    ExpiredVerificationCodeError,
    NotFoundError,
    NotVerifiedError,
)
from app.core.logger import get_logger
from app.core.security import (
    extract_user_data,
    generate_token_for_existing_user,
    generate_token_for_new_user,
    generate_verification_token,
)
from app.core.settings import settings
from app.repository.activity_log_repository import ActivityLogRepository
from app.repository.email_verification_repository import EmailVerificationRepository
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.user_repository import UserRepository
from app.repository.user_subscription_repository import UserSubscriptionRepository
from app.schema.activity_log_schema import ActivityLogSchema
from app.schema.auth_schema import UserEmailVerification, VerifyToken
from app.schema.user_schema import UserLogin
from app.service.base_service import BaseService
from app.util.enums import ActiveStatus, ActivityLogClass, ActivityLogType, RoleType

log = get_logger()


class AuthService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_repository: EmailVerificationRepository,
        user_subscription_repository: UserSubscriptionRepository,
        subscription_repository: SubscriptionRepository,
        activity_log_repository: ActivityLogRepository,
    ):
        self.user_repository = user_repository
        self.email_verification_repository = email_verification_repository
        self.user_subscription_repository = user_subscription_repository
        self.subscription_repository = subscription_repository
        self.activity_log_respository = activity_log_repository
        super().__init__(user_repository)

    def login(self, login_info: UserLogin, request: Request):
        try:
            db_user = self.user_repository.get_user_by_email_address(
                login_info.email_address
            )
            log.info("User found", extra={"user": db_user})
            if db_user is None:
                raise NotFoundError(detail="User not found")
            if db_user.verifiedAt is None:
                raise NotVerifiedError(detail="User email not verified")
            if db_user.status == ActiveStatus.DEACTIVATED:
                raise AuthError(detail="User account is deactivated")
            if db_user.status == ActiveStatus.INACTIVE:
                raise AuthError(detail="User is not active")

            user = extract_user_data(db_user)

            user_plan = self.user_subscription_repository.get_user_subscription(
                user.get("email_address")
            )

            if user_plan and user_plan.subscription_code:
                paystack_subscription = (
                    self.subscription_repository.get_paystack_subscription(
                        user_plan.subscription_code
                    )
                )

                user_package = {
                    "package_name": paystack_subscription["plan"]["name"],
                    "package_items": paystack_subscription["package_items"],
                }

            else:
                user_package = {
                    "package_name": FREE_PACKAGE,
                    "package_items": FREE_PACKAGE_ITEMS,
                }

            access_token, expiration_datetime = generate_token_for_existing_user(
                login_info, db_user
            )

            log.info("Access token generated successfully")

            business_profile_uuid = user.get("business_profile_uuid")

            print("business_profile_uuid", business_profile_uuid)

            if user.get("role") == RoleType.CUSTOMER:
                user["package"] = user_package
                schema = ActivityLogSchema(
                    user_uuid=str(user.get("uuid")),
                    business_profile_uuid=str(user.get("business_profile_uuid"))
                    if user.get("business_profile_uuid")
                    else None,
                    activity_class=ActivityLogClass.USER,
                    activity_type=ActivityLogType.SIGN_IN,
                    activity_title=activity_log_constants.SIGN_IN,
                    activity_description=activity_log_constants.SIGN_IN_DESC.format(
                        full_name=user.get("first_name") + " " + user.get("last_name")
                    ),
                    ip_address=request.client.host,
                )
                self.activity_log_respository.create(schema)
            if user.get("role") == RoleType.ADMIN:
                schema = ActivityLogSchema(
                    user_uuid=str(user.get("uuid")),
                    business_profile_uuid=str(user.get("business_profile_uuid"))
                    if user.get("business_profile_uuid")
                    else None,
                    activity_class=ActivityLogClass.ADMIN,
                    activity_type=ActivityLogType.SIGN_IN,
                    activity_title=activity_log_constants.SIGN_IN,
                    activity_description=activity_log_constants.SIGN_IN_DESC.format(
                        full_name=user.get("first_name") + " " + user.get("last_name")
                    ),
                    ip_address=request.client.host,
                )
                self.activity_log_respository.create(schema)
            login_result = {
                "access_token": access_token,
                "expiration": expiration_datetime,
                "user": user,
            }
            return login_result
        except Exception as e:
            raise e

    def decode_access_token(self, token_data: VerifyToken):
        try:
            payload = jwt.decode(
                token_data.Token,
                settings.SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM],
            )
            if payload is None:
                log.error("Invalid jwt token in payload")
                raise AuthError(detail="Could not decode token")
            email = payload.get("sub")
        except (jwt.JWTError, jwt.ExpiredSignatureError) as e:
            log.error(e)
            raise AuthError(detail="Could not decode token")
        except Exception as e:
            raise e

        user = self.user_repository.get_user_by_email_address(email)
        if not user:
            raise NotFoundError(detail="User not found")

        return extract_user_data(user)

    def verify_token(self, token_data: VerifyToken):
        user_token = self.email_verification_repository.get_by_token(token_data.Token)
        if user_token:
            current_datetime = datetime.now()
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            current_date = current_datetime.strftime(date_format)
            expiry_date = user_token.expiry_date

            # check if token has expired
            if expiry_date > current_date:
                user_data = self.user_repository.read_by_uuid(user_token.user_uuid)

                if not user_data:
                    raise NotFoundError(detail="User not found")
                else:
                    access_token, expiration_datetime = generate_token_for_new_user(
                        user_email=user_data.email_address, db_user=user_data
                    )
                    log.info("Access token generated successfully")

                    # update user table verifiedAt to current date
                    self.user_repository.update_attr(
                        user_token.user.id, "verifiedAt", datetime.now()
                    )
                    log.info("User verifiedAt updated successfully")

                    # delete user token from token table
                    self.email_verification_repository.delete_by_verification_token(
                        token_data.Token
                    )
                    log.info("User token deleted successfully")

                    # Return the access token to the client
                    return {
                        "access_token": access_token,
                        "expiration": expiration_datetime,
                        "token_type": "bearer",
                        "detail": "User verified successfully",
                        "account_type": user_data.account_type,
                    }
            else:
                # delete expired verification token
                self.email_verification_repository.delete_by_verification_token(
                    token_data.Token
                )

                raise ExpiredVerificationCodeError(detail="Verification code expired")
        else:
            raise NotFoundError(detail="Verification token not found")

    def verify_user_email(self, user: UserEmailVerification):
        try:
            # check if user already verified
            db_user = self.user_repository.read_by_uuid(user.uuid)
            if db_user:
                if db_user.verifiedAt is None:
                    # check if token already generated
                    verified_user = (
                        self.email_verification_repository.read_by_user_uuid(user.uuid)
                    )
                    if verified_user:
                        log.info(
                            "User already has a verification token",
                            extra={"user": verified_user.user_uuid},
                        )
                        # Delete old verification token
                        self.email_verification_repository.delete_by_user_uuid(
                            user.uuid
                        )

                    # Generate new verification token
                    verify_token = generate_verification_token()
                    token_detail = {
                        "user_uuid": user.uuid,
                        "verification_token": verify_token,
                        # "expiry_date": expiry_time  # Save the expiry time to the database
                    }
                    return token_detail
                else:
                    raise AlreadyVerifiedError(detail="User already verified")
            else:
                raise NotFoundError(detail="User not found")
        except Exception as e:
            raise e
