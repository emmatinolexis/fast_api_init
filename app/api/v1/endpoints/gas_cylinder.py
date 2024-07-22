from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.gas_cylinder_service import GasCylinderService
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/gas_cylinder",
    tags=["Gas Cylinder"],
)
msg_prefix = "gas cylinder"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_gas_cylinder_handler(
    service: GasCylinderService = Depends(
        Provide[Container.gas_cylinder_event_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/events", response_class=ORJSONResponse)
@inject
async def get_all_gas_event_handler(
    service: GasCylinderEventService = Depends(
        Provide[Container.gas_cylinder_event_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
