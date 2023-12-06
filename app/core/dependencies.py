import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import jwt
from pydantic import ValidationError

from app.core.container import Container
from app.core.exceptions import AuthError
from app.core.security import JWTBearer, verify_token
from app.model.user import User
from app.service.user_service import UserService

log = structlog.get_logger()


@inject
def get_current_user(
    token: str = Depends(JWTBearer()),
    service: UserService = Depends(Provide[Container.user_service]),
) -> User:
    try:
        token_data = verify_token(token)
    except Exception as e:
        log.error(e)
        raise AuthError(detail="Could not validate credentials")

    current_user: User = service.get_user_by_email_address(token_data.username)
    if not current_user:
        raise AuthError(detail="User not found")
    log.info("Current user in session", user=current_user.email_address)
    return current_user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise AuthError("Inactive user")
    return current_user


def get_current_user_with_no_exception(
    token: str = Depends(JWTBearer()),
    service: UserService = Depends(Provide[Container.user_service]),
) -> User:
    try:
        token_data = verify_token(token)
    except (jwt.JWTError, ValidationError):
        return None

    current_user: User = service.get_user_by_email_address(token_data.username)
    if not current_user:
        return None
    log.info("Current user in session", user=current_user)
    return current_user
