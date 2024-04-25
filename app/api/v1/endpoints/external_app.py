from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.external_app_schema import ExternalAppGenerateTokenPayload
from app.service.external_app_service import ExternalAppService
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/external_app",
    tags=["External Apps"],
)
msg_prefix = "external_app"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_external_app_handler(
    service: ExternalAppService = Depends(Provide[Container.external_app_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def generate_app_service_token(
    payload: ExternalAppGenerateTokenPayload,
    service: ExternalAppService = Depends(Provide[Container.external_app_service]),
):
    try:
        token = service.generate_token(payload)
        return send_data(token)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/generate_token", response_class=ORJSONResponse)
@inject
async def create_app_handler(
    payload: ExternalAppGenerateTokenPayload,
    service: ExternalAppService = Depends(Provide[Container.external_app_service]),
    # current_user: User = Depends(get_current_user),
):
    try:
        app = service.generate_token(payload)
        return send_data(app)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
