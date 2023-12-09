import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError, NotFoundError
from app.core.security import extract_user_data
from app.model.user import User
from app.schema.user_schema import UpdateUser
from app.schema.user_schema import User as UserSchema
from app.service.user_service import UserService
from app.util.utils import send_data

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

log = structlog.get_logger()


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_user(
    user: UserSchema, service: UserService = Depends(Provide[Container.user_service])
):
    try:
        found_user = service.get_user_by_email_address(user.email_address)
        if found_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )
        return send_data(service.create_user(user))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create user")


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
        log.error(e)
        raise InternalServerError(detail="Could not get users")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_user(
    uuid: str,
    user: UpdateUser,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.update_user_by_uuid(uuid, user))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update user")


@router.get("/{email_address}", response_class=ORJSONResponse)
@inject
async def get_user_by_email(
    email_address: str, service: UserService = Depends(Provide[Container.user_service])
):
    try:
        user = service.get_user_by_email_address(email_address)
        if not user:
            raise NotFoundError(detail="User Not Found")
        return send_data(extract_user_data(user))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get user")
