from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestError, NotFoundError
from app.model.user import User
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.gas_cylinder_service import GasCylinderService
from app.service.gas_device_service import GasDeviceService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

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


@router.patch("/{gas_cylinder_id}/link/{gas_device_id}", response_class=ORJSONResponse)
@inject
async def link_gas_cylinder_to_device_handler(
    gas_device_id: str,
    gas_cylinder_id: str,
    service: GasCylinderService = Depends(Provide[Container.gas_cylinder_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        gas_cylinder = service.link_to_gas_device(gas_cylinder_id, gas_device_id)
        return send_data(gas_cylinder)
    except (NotFoundError, BadRequestError) as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))
    except Exception as e:
        msg = messages.LINK_FAILED + f"{msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{gas_cylinder_id}/unlink", response_class=ORJSONResponse)
@inject
async def unlink_gas_cylinder_from_device_handler(
    gas_cylinder_id: str,
    service: GasCylinderService = Depends(Provide[Container.gas_cylinder_service]),
    gas_device_service: GasDeviceService = Depends(
        Provide[Container.gas_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.unlink_gas_cylinder(gas_cylinder_id)
        return send_info(messages.CYLINDER_UNLINKED)
    except (NotFoundError, BadRequestError) as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"{messages.UNLINK_FAILED}: {str(e)}"
        return send_internal_server_error(
            user_msg=messages.INTERNAL_SERVER_ERROR, error=error_msg
        )
