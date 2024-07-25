from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.gas_cylinder_schema import (
    CreateGasDevice,
    UpdateGasDevice,
    UserCreateGasDevice,
)
from app.service.gas_device_service import GasDeviceService
from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/gas_device",
    tags=["Gas Device"],
)


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
        if user:
            if user.get("account_type") == AccountType.INDIVIDUAL:
                return send_data(
                    service.add(
                        UserCreateGasDevice(
                            device_name=payload.device_name,
                            user_uuid=str(user.get("uuid")),
                            serial_number=payload.serial_number,
                        )
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    service.add(
                        UserCreateGasDevice(
                            device_name=payload.device_name,
                            business_uuid=str(user.get("business_profile").uuid),
                            user_uuid=str(user.get("uuid")),
                            serial_number=payload.serial_number,
                        )
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_id}"
            return send_internal_server_error(user_msg=msg, error=msg)
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
