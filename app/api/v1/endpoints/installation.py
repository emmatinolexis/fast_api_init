from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.installation_schema import InstallationPayload, AssignInstallerPayload

from app.service.installation_service import InstallationService
from app.util.utils import send_data, send_internal_server_error, send_client_side_error, send_data_with_info


router = APIRouter(
    prefix="/installation",
    tags=["installation"],
)
msg_prefix = "installation"


@router.get(
    "/installers", response_class=ORJSONResponse
)
@inject
async def get_installers_handler(
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        installers = service.fetch_all_installers()
        return send_data(installers)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installers.", error=e
        )


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_installation_handler(
    payload: InstallationPayload,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        installation = service.get_installation_by_order_uuid(payload.order_uuid)
        if installation:
            return send_client_side_error(messages.INSTALLATION_CREATED_MSG)

        installation = service.create_installation(payload)
        return send_data(installation)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/assign_installer", response_class=ORJSONResponse)
@inject
async def assign_installer_handler(
    payload: AssignInstallerPayload,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        installation = service.get_installation(payload.installation_uuid)
        if not installation:
            return send_client_side_error(messages.INSTALLATION_NOT_FOUND_MSG)

        installation_to_update = service.assign_installer_to_installation(payload)

        return send_data_with_info(installation_to_update, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_installations_handler(
    service: InstallationService = Depends(Provide[Container.installation_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),

):
    try:
        installations = service.fetch_installations(page, page_size)
        return send_data(installations)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.get("/installer/installations/{installer_uuid}", response_class=ORJSONResponse)
@inject
async def get_installer_installations_handler(
    installer_uuid: str,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),

):
    try:
        installations = service.fetch_installations(page, page_size, installer_uuid)
        return send_data(installations)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.get("/installation/{installation_uuid}", response_class=ORJSONResponse)
@inject
async def get_installation_handler(
    installation_uuid: str,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        installation = service.get_installation(installation_uuid)
        if not installation:
            send_client_side_error(messages.INSTALLATION_NOT_FOUND_MSG)
        return send_data(installation)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


# @router.get("/configure", response_class=ORJSONResponse)
# @inject
# async def configure_device_handler(
#     payload: InstallationPayload,
#     service: InstallationService = Depends(Provide[Container.installation_service]),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         installation = service.get_installation(installation_uuid)
#         if not installation:
#             send_client_side_error(messages.INSTALLATION_NOT_FOUND_MSG)
#         return send_data(installation)
#     except Exception as e:
#         return send_internal_server_error(
#             user_msg="Failed to fetch installations.", error=e
#         )