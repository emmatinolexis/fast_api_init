from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.third_party_app_schema import (
    ThirdPartyAppPayload,
    ThirdPartyAppUserPayload,
)
from app.service.third_party_app_service import ThirdPartyAppService
from app.service.third_party_app_user_service import ThirdPartyAppUserService
from app.util.utils import (
    send_data,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/third_party_app",
    tags=["third party apps and user"],
)
msg_prefix = "third_party_app"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_third_party_apps_handler(
    service: ThirdPartyAppService = Depends(Provide[Container.third_party_app_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_third_party_app_handler(
    payload: ThirdPartyAppPayload,
    service: ThirdPartyAppService = Depends(Provide[Container.third_party_app_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        app = service.add(payload)
        return send_data(app)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{app_uuid}", response_class=ORJSONResponse)
@inject
async def update_third_party_app_handler(
    app_uuid: str,
    payload: ThirdPartyAppPayload,
    service: ThirdPartyAppService = Depends(Provide[Container.third_party_app_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        app = service.patch_by_uuid(app_uuid, payload)
        return send_data(app)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/users", response_class=ORJSONResponse)
@inject
async def get_all_third_party_apps_users_handler(
    service: ThirdPartyAppUserService = Depends(
        Provide[Container.third_party_app_user_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_app_users())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/users", response_class=ORJSONResponse)
@inject
async def create_third_party_app_user_handler(
    payload: ThirdPartyAppUserPayload,
    service: ThirdPartyAppUserService = Depends(
        Provide[Container.third_party_app_user_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        app = service.add(payload)
        return send_data(app)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/users/{app_user_uuid}", response_class=ORJSONResponse)
@inject
async def update_third_party_app_user_handler(
    app_user_uuid: str,
    payload: ThirdPartyAppUserPayload,
    service: ThirdPartyAppUserService = Depends(
        Provide[Container.third_party_app_user_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        app = service.patch_by_uuid(app_user_uuid, payload)
        return send_data(app)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
