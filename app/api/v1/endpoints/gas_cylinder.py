from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.gas_cylinder_schema import LinkGasCylinder, UpdateGasDevice
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.gas_cylinder_service import GasCylinderService
from app.service.gas_device_service import GasDeviceService
from app.util.enums import ActiveStatus, DeviceStatus
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
    gas_device_service: GasDeviceService = Depends(
        Provide[Container.gas_device_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        # Fetch gas device and cylinder by UUID
        gas_device = gas_device_service.get_by_uuid(gas_device_id)
        gas_cylinder = service.get_by_uuid(gas_cylinder_id)

        # Validate existence of gas device and cylinder
        if not gas_device:
            msg = f"{messages.GAS_DEVICE_NOT_FOUND} {gas_device_id}"
            return send_internal_server_error(user_msg=msg, error=msg)

        if not gas_cylinder:
            msg = f"{messages.GAS_CYLINDER_NOT_FOUND} {gas_cylinder_id}"
            return send_internal_server_error(user_msg=msg, error=msg)

        # Validate user's authorization to link the gas device
        if gas_device.user_uuid != current_user.uuid:
            return send_client_side_error(
                user_msg=messages.ACTION_NOT_ALLOWED,
                error=messages.ACTION_NOT_ALLOWED,
            )

        # Validate status of gas cylinder and device
        if gas_cylinder.status == ActiveStatus.INACTIVE:
            return send_client_side_error(
                user_msg=messages.GAS_CYLINDER_INACTIVE,
                error=messages.GAS_CYLINDER_INACTIVE,
            )

        if gas_device.status == DeviceStatus.ASSIGNED:
            return send_internal_server_error(
                user_msg=messages.DEVICE_ALREADY_ASSIGNED,
                error=messages.DEVICE_ALREADY_ASSIGNED,
            )

        # Link gas cylinder to gas device and update statuses
        service.patch_by_uuid(
            gas_cylinder.uuid, LinkGasCylinder(gas_device_uuid=gas_device.uuid)
        )
        gas_device_service.patch_by_uuid(
            gas_device.uuid, UpdateGasDevice(status=DeviceStatus.ASSIGNED)
        )

        return send_data(gas_cylinder)

    except Exception as e:
        error_msg = messages.LINK_FAILED + f"{msg_prefix} to device"
        return send_internal_server_error(user_msg=error_msg, error=e)


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
        # Fetch gas cylinder by UUID
        gas_cylinder = service.get_by_uuid(gas_cylinder_id)

        # Validate existence of gas cylinder
        if not gas_cylinder:
            msg = f"{messages.GAS_CYLINDER_NOT_FOUND} {gas_cylinder_id}"
            return send_internal_server_error(user_msg=msg, error=msg)

        # Validate user's authorization to unlink the gas cylinder
        if gas_cylinder.user_uuid != current_user.uuid:
            return send_client_side_error(
                user_msg=messages.ACTION_NOT_ALLOWED,
                error=messages.ACTION_NOT_ALLOWED,
            )

        # Unlink gas cylinder from gas device and update statuses
        gas_device_uuid = gas_cylinder.gas_device_uuid
        if gas_device_uuid:
            gas_device_service.patch_by_uuid(
                gas_device_uuid, UpdateGasDevice(status=DeviceStatus.NOT_ASSIGNED)
            )
        else:
            return send_client_side_error(
                user_msg=messages.ALREADY_UNLINKED,
                dev_msg=messages.ALREADY_UNLINKED,
            )

        service.unlink_gas_device(gas_cylinder.uuid)

        return send_info(messages.CYLINDER_UNLINKED)

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"{messages.UNLINK_FAILED}: {str(e)}"
        return send_internal_server_error(
            user_msg=messages.INTERNAL_SERVER_ERROR, error=error_msg
        )
