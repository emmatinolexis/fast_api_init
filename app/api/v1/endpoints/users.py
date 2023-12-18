import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import EmailStr

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.core.security import JWTBearer, extract_user_data
from app.model.user import User
from app.schema.user_schema import UpdateUserPayload, UserPayload
from app.service.user_service import UserService
from app.util.utils import (
    ADMIN_USER_ROLE,
    allow_admins_only,
    send_client_side_error,
    send_data,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

log = structlog.get_logger()
msg_prefix = "user"


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_user_handler(
    payload: UserPayload,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        found_user = service.get_user_by_email_address(payload.email_address)
        if found_user:
            return send_client_side_error(
                user_msg=f"User already exists : {payload.email_address}",
            )
        user = service.create_user(payload)
        return send_data(user)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_users(
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        users = service.get_list()
        users_info = [extract_user_data(user) for user in users]
        return send_data(users_info)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_user(
    uuid: str,
    payload: UpdateUserPayload,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.update_user_by_uuid(uuid, payload)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + uuid,
            )
        return send_data(extract_user_data(user))
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.USER_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/{email_address}", dependencies=[allow_admins_only], response_class=ORJSONResponse
)
@inject
async def get_user_by_email(
    email_address: EmailStr,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user = service.get_user_by_email_address(email_address)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + email_address
            )
        return send_data(extract_user_data(user))
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
