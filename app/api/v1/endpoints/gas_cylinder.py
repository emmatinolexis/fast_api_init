from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestError, NotFoundError
from app.model.user import User
from app.schema.gas_cylinder_schema import (
    CreateGasCylinder,
    CreateGasCylinderPayload,
    GasEventPayload,
)
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.gas_cylinder_service import GasCylinderService
from app.service.gas_device_service import GasDeviceService
from app.service.user_service import UserService
from app.util.enums import AccountType, DeviceStatus
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


@router.post("/event", response_class=ORJSONResponse)
@inject
async def create_gas_cylinder_event_handler(
    gas_cylinder: GasEventPayload,
    service: GasCylinderEventService = Depends(
        Provide[Container.gas_cylinder_event_service]
    ),
):
    try:
        created_gas_cylinder = service.add(gas_cylinder)
        return send_data(created_gas_cylinder)
    except Exception as e:
        msg = f"{messages.CREATE_FAILED} - {str(e)}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_gas_cylinder_handler(
    user_uuid: str,
    gas_cylinder: CreateGasCylinderPayload,
    service: GasCylinderService = Depends(Provide[Container.gas_cylinder_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)
        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + user_uuid,
                dev_msg=messages.USER_NOT_FOUND + user_uuid,
            )

        gas_cylinder_data = gas_cylinder.dict()

        if user.get("account_type") == AccountType.BUSINESS:
            gas_cylinder_data["business_id"] = user.get("id")

        gas_cylinder_data["user_uuid"] = user_uuid
        new_gas_cylinder = CreateGasCylinder(**gas_cylinder_data)

        created_gas_cylinder = service.add(new_gas_cylinder)
        return send_data(created_gas_cylinder)
    except Exception as e:
        msg = f"{messages.CREATE_FAILED} - {str(e)}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{gas_cylinder_id}/link/{gas_device_id}", response_class=ORJSONResponse)
@inject
async def link_gas_cylinder_to_device_handler(
    gas_device_id: str,
    gas_cylinder_id: str,
    service: GasCylinderService = Depends(Provide[Container.gas_cylinder_service]),
    device_service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        device = device_service.get_device_by_uuid(gas_device_id)
        if not device:
            return send_client_side_error(
                user_msg=messages.GAS_DEVICE_NOT_FOUND + gas_device_id,
                dev_msg=messages.GAS_DEVICE_NOT_FOUND + gas_device_id,
            )

        gas_cylinder = service.get_by_uuid(gas_cylinder_id)
        if not gas_cylinder:
            return send_client_side_error(
                user_msg=messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_id,
                dev_msg=messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_id,
            )

        if device.status == DeviceStatus.ASSIGNED:
            return send_client_side_error(
                user_msg=messages.DEVICE_ALREADY_ASSIGNED,
                dev_msg=messages.DEVICE_ALREADY_ASSIGNED,
            )

        if gas_cylinder.gas_device_uuid:
            return send_client_side_error(
                user_msg=messages.CYLINDER_ALREADY_LINKED,
                dev_msg=messages.CYLINDER_ALREADY_LINKED,
            )

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
        gas_cylinder = service.get_by_uuid(gas_cylinder_id)
        if not gas_cylinder:
            return send_client_side_error(
                user_msg=messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_id,
                dev_msg=messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_id,
            )

        if not gas_cylinder.gas_device_uuid:
            return send_client_side_error(
                user_msg=messages.ALREADY_UNLINKED,
                dev_msg=messages.ALREADY_UNLINKED,
            )

        service.unlink_gas_cylinder(gas_cylinder_id)
        return send_info(messages.CYLINDER_UNLINKED)
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"{messages.UNLINK_FAILED}: {str(e)}"
        return send_internal_server_error(
            user_msg=messages.INTERNAL_SERVER_ERROR, error=error_msg
        )
