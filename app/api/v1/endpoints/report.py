from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.service.asset_service import AssetService
from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)
msg_prefix = "Reports"


@router.get("/distance_speed_report/{user_uuid}", response_class=ORJSONResponse)
@inject
async def generate_distance_traveled_report_handler(
    user_uuid: str,
    start_date: str = Query(
        description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(description="End date should be in the format dd/mm/yyyy"),
    report_service: AssetService = Depends(Provide[Container.asset_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)
        if user:
            if user.get("account_type") == AccountType.INDIVIDUAL:
                return send_data(
                    report_service.generate_distance_speed_report(
                        user_uuid=user.get("uuid"),
                        start_date=start_date,
                        end_date=end_date,
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    report_service.generate_distance_speed_report(
                        business_uuid=user.get("business_profile").uuid,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
