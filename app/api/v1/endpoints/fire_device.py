from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import BadRequestError, NotFoundError
from app.model.user import User
from app.schema.fire_device_schema import CreateFireDevice
from app.service.gas_device_service import GasDeviceService
from app.util.utils import (
    load_fire_device_serial_number_from_file,
    send_client_side_error,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/fire_device",
    tags=["fire_device"],
)


@router.post("/load_csv", response_class=ORJSONResponse)
@inject
async def bulk_upload_fire_devices(
    file_url: str,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    current_user: User = Depends(get_current_user_with_permission("create_pyrogaurd_device")),
):
    try:
        serial_numbers = load_fire_device_serial_number_from_file(file_url=file_url)
        message = service.load_fire_devices(serial_numbers, current_user)
        return send_info(message)
    except ValueError as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))
    except Exception as e:
        msg = "Failed to load fire devices"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/building/{building_uuid}", response_class=ORJSONResponse)
@inject
async def add_fire_device(
    building_uuid: str,
    payload: CreateFireDevice,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    current_user: User = Depends(get_current_user_with_permission("create_pyrogaurd_device")),
):
    try:
        message = service.add_fire_device_to_building(
            building_uuid, payload, current_user
        )
        return send_info(message)
    except (NotFoundError, BadRequestError) as e:
        return send_client_side_error(user_msg=str(e.detail), dev_msg=str(e.detail))
    except Exception as e:
        msg = "Failed to add fire device"
        return send_internal_server_error(user_msg=msg, error=e)
