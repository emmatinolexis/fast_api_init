from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.gas_cylinder_schema import (
    CreateGasDevice,
    UpdateGasDevice,
    UserCreateGasDevice,
)
from app.service.gas_device_service import GasDeviceService
from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import (
    load_gas_device_serial_number_from_csv,
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/gas_device",
    tags=["Gas Device"],
)


@router.post("/load_csv", response_class=ORJSONResponse)
@inject
async def load_csv_handler(
    csv_url: str,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    user: User = Depends(get_current_user),
):
    try:
        serial_numbers = load_gas_device_serial_number_from_csv(csv_url=csv_url)
        return send_info(service.load_csv(serial_numbers, user))
    except Exception as e:
        msg = messages.CSV_LOAD_FAILED
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_gas_devices_handler(
    serial_number: str = Query(None, description="Serial number of the gas device"),
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_devices(serial_number))
    except Exception as e:
        msg = messages.GET_FAILED + " gas devices"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/{user_id}", response_class=ORJSONResponse)
@inject
async def create_gas_device_handler(
    user_id: str,
    payload: CreateGasDevice,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_id)

        if user.get("account_type") == AccountType.INDIVIDUAL:
            data = service.create_device(user_id=user_id, payload=payload)
        if user.get("account_type") == AccountType.BUSINESS:
            data = service.create_device(
                business_profile_uuid=user.get("business_profile").uuid,
                payload=payload,
                user_uuid=user_id,
            )
            return send_data(data)
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_id}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + " gas device"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{device_uuid}", response_class=ORJSONResponse)
@inject
async def update_device_handler(
    device_uuid: str,
    payload: UpdateGasDevice,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
):
    try:
        device = service.get_device_by_uuid(device_uuid)

        if not device:
            msg = f"{messages.GAS_DEVICE_NOT_FOUND} "
            return send_client_side_error(user_msg=msg)
        return send_data(service.patch_by_uuid(device_uuid, payload))
    except Exception as e:
        msg = messages.UPDATE_FAILED + " gas device"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_id}", response_class=ORJSONResponse)
@inject
async def get_gas_devices_by_user_handler(
    user_id: str,
    service: GasDeviceService = Depends(Provide[Container.gas_device_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_id)

        if not user:
            msg = f"{messages.USER_NOT_FOUND} {user_id}"
            return send_client_side_error(user_msg=msg, status_code=404)

        if user.get("account_type") == AccountType.INDIVIDUAL:
            data = service.get_user_devices(user_id)

        if user.get("account_type") == AccountType.BUSINESS:
            data = service.get_business_devices(user.get("business_profile").uuid)

            return send_data_with_info(data, messages.GET_SUCCESS + " gas devices")
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.GET_FAILED + " gas devices"
        return send_internal_server_error(user_msg=msg, error=e)
