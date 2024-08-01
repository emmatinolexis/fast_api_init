from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core import messages
from app.core.container import Container
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.user_service import UserService
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/gas_report",
    tags=["gas report"],
)


@router.get("/{user_uuid}")
@inject
async def get_gas_report(
    user_uuid: str,
    start_date: str,
    end_date: str,
    service: GasCylinderEventService = Depends(
        Provide[Container.gas_cylinder_event_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user = user_service.get_by_uuid(user_uuid)
        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND,
                error=f"User with uuid {user_uuid} not found",
            )

        data = service.generate_report(
            user_uuid=user_uuid,
            start_date=start_date,
            end_date=end_date,
        )

        return send_data(data)
    except Exception as e:
        return send_internal_server_error(user_msg="Failed to get gas report", error=e)
