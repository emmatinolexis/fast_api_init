import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.exceptions import InternalServerError
from app.core.security import verify_token_frontend
from app.core.settings import settings
from app.schema.auth_schema import UserEmailVerification, VerifyToken
from app.schema.user_schema import UserLogin
from app.service.auth_service import AuthService
from app.util.email import send_email
from app.util.utils import send_data, send_info

router = APIRouter(
    prefix="",
    tags=["authentication"],
)

log = structlog.get_logger()


@router.post("/decode_token", response_class=ORJSONResponse)
@inject
async def decode_access_token(
    token_data: VerifyToken,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        return send_data(service.decode_access_token(token_data))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not decode token")


# This endpoint serves a crucial security function for users who choose to register via email.
# Upon successful registration, the user's access token is stored within a cookie.
# To ensure the legitimacy of the token and prevent unauthorized generation of tokens,
# the token within the cookie undergoes a verification process.
@router.post("/verify_token_frontend", response_class=ORJSONResponse)
@inject
async def verify_token_frontend_handler(token_data: VerifyToken):
    if verify_token_frontend(token_data.Token):
        return send_data("Token is valid")
    else:
        error_message = "Token is invalid or expired"
        log.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )


@router.post("/verify_token", response_class=ORJSONResponse)
@inject
async def verify_token(
    token_data: VerifyToken,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        return send_data(service.verify_token(token_data))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not verify token")


@router.post("/verify_email", response_class=ORJSONResponse)
@inject
async def verify_user_email(
    user: UserEmailVerification,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        token_detail = service.verify_user_email(user)
        log.info("token", token=token_detail)
        # save generated token into db
        user, token = service.user_repository.create_verification_token(
            user_verify=user, verification_token=token_detail
        )
        log.info("user email verified", user=user.email_address)
        if user and token:
            try:
                # send verification email
                await send_email(
                    subject=settings.MAIL_SUBJECT,
                    recipient_name=user.first_name,
                    email=user.email_address,
                    message=settings.MAIL_VERIFICATION_MESSAGE,
                    token=token,
                )
            except Exception as e:
                log.error("error sending email", error=str(e))
                raise InternalServerError(detail="Could not send verification email")
        return send_info("Verification token generated successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not generate verification token")


@router.post("/login", response_class=ORJSONResponse)
@inject
async def login(
    user: UserLogin, service: AuthService = Depends(Provide[Container.auth_service])
):
    try:
        return send_data(service.login(user))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not login user")
