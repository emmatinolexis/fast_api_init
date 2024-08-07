from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.fuel_log_schema import FuelLogSchema
from app.service.fuel_log_service import FuelLogService
from app.service.user_service import UserService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/fuel_logs",
    tags=["fuel_logs"],
)
msg_prefix = "fuel_log"


@router.post("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_fuel_log_handler_for_individual(
    user_uuid: str,
    payload: FuelLogSchema,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)

        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND, status_code=404
            )

        data = service.create_individual_fuel_log(payload, user_uuid)

        return send_data(data)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
