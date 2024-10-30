from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.installation_schema import InstallationPayload
from app.schema.user_schema import InstallerResponse
from app.service.installation_service import InstallationService
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/installation",
    tags=["installation"],
)
msg_prefix = "installation"


@router.get(
    "/installers", response_model=List[InstallerResponse], response_class=ORJSONResponse
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
        return send_internal_server_error(user_msg="Failed to fetch installers.", error=e)
    
@router.post("/", response_class=ORJSONResponse)
@inject
async def create_installation_handler(
    payload: InstallationPayload,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        installation = service.create_installation(payload)
        return send_data(installation)
    except ValueError as ve:
        return ORJSONResponse({"detail": str(ve)}, status_code=400)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)





