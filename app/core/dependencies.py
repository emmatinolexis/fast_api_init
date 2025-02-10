from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from jose import jwt
from pydantic import ValidationError

from app.core.container import Container
from app.core.exceptions import AuthError
from app.core.logger import get_logger
from app.core.security import JWTBearer, verify_third_party_token, verify_token
from app.model.external_app import ExternalApp
from app.model.user import User
from app.service.external_app_service import ExternalAppService
from app.service.user_service import UserService
from app.util.enums import ActiveStatus
from app.util.utils import (
    ADMIN_USER_ROLE,
    CUSTOMER_USER_ROLE,
    THIRD_PARTY_APP_ROLE,
    check_permission,
)

log = get_logger()


def get_current_user_with_permission(permission: str):
    async def dependency(
        token: str = Depends(
            JWTBearer(allowed_roles=[ADMIN_USER_ROLE, CUSTOMER_USER_ROLE])
        ),
        service: UserService = Depends(Provide[Container.user_service]),
    ):
        return await get_user_permission(
            token=token, service=service, permission=permission
        )

    return dependency


@inject
async def get_current_user(
    token: str = Depends(
        JWTBearer(allowed_roles=[ADMIN_USER_ROLE, CUSTOMER_USER_ROLE])
    ),
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        token_data = verify_token(token)
    except Exception as e:
        log.error(e)
        raise AuthError(detail="Could not validate credentials")

    current_user: User = await service.get_user_by_email_address(token_data.username)

    if not current_user:
        raise AuthError(detail="User not found")
    log.info(
        f"Current user in session {current_user.email_address}",
        extra={"email_address": current_user.email_address},
    )

    if (
        current_user.status == ActiveStatus.INACTIVE
        or current_user.status == ActiveStatus.DEACTIVATED
    ):
        raise AuthError(detail="User is not active or deactivated")

    return current_user


@inject
async def get_user_permission(
    token: str = Depends(
        JWTBearer(allowed_roles=[ADMIN_USER_ROLE, CUSTOMER_USER_ROLE])
    ),
    service: UserService = Depends(Provide[Container.user_service]),
    permission: str = None,
):
    try:
        token_data = verify_token(token)
    except Exception as e:
        log.error(e)
        raise AuthError(detail="Could not validate credentials")

    current_user: User = await service.get_user_by_email_address(token_data.username)

    if not current_user:
        raise AuthError(detail="User not found")
    log.info(
        f"Current user in session {current_user.email_address}",
        extra={"email_address": current_user.email_address},
    )

    if (
        current_user.status == ActiveStatus.INACTIVE
        or current_user.status == ActiveStatus.DEACTIVATED
    ):
        raise AuthError(detail="User is not active or deactivated")

    if permission:
        check_permission(current_user.user_role.permissions, permission)

    return current_user


@inject
def check_user_permission(
    current_user,
    permission_name: str = None,
):
    for permission in current_user.user_role.permissions:
        if permission.get("permission_name") == permission_name:
            return True
    # Raise a 403 Forbidden error if the permission is not found
    raise HTTPException(status_code=403, detail="Not Authorized")


@inject
async def get_current_app_service(
    token: str = Depends(JWTBearer(allowed_roles=[THIRD_PARTY_APP_ROLE])),
    service: ExternalAppService = Depends(Provide[Container.external_app_service]),
) -> ExternalApp:
    try:
        token_data = verify_third_party_token(token)
    except Exception as e:
        log.error(e)
        raise AuthError(detail="Could not validate app keys")
    current_app_service: ExternalApp = await service.get_app_service_by_secret_key(
        token_data.secret_key
    )
    if not current_app_service:
        raise AuthError(detail="App service not found")
    log.info(
        "Current app service in session",
        extra={"secret_key": current_app_service.secret_key},
    )
    return current_app_service


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise AuthError("Inactive user")
    return current_user


def get_current_user_with_no_exception(
    token: str = Depends(
        JWTBearer(allowed_roles=[ADMIN_USER_ROLE, CUSTOMER_USER_ROLE])
    ),
    service: UserService = Depends(Provide[Container.user_service]),
) -> User:
    try:
        token_data = verify_token(token)
    except (jwt.JWTError, ValidationError):
        return None

    current_user: User = service.get_user_by_email_address(token_data.username)
    if not current_user:
        return None
    log.info(
        f"Current user in session {current_user.email_address}",
        extra={"user", current_user},
    )
    return current_user
