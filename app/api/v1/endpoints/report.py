from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.report_schema import SmartReportInput, SmartReportPayload
from app.service.asset_service import AssetService

from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)
msg_prefix = "Report"


@router.get("/distance_speed_report/{user_uuid}", response_class=ORJSONResponse)
@inject
async def generate_distance_traveled_report_handler(
    user_uuid: str,
    asset_uuid: str = None,
    asset_type_uuid: str = None,
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
                        asset_uuid=asset_uuid,
                        asset_type_uuid=asset_type_uuid,
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    report_service.generate_distance_speed_report(
                        business_uuid=user.get("business_profile").uuid,
                        start_date=start_date,
                        end_date=end_date,
                        asset_uuid=asset_uuid,
                        asset_type_uuid=asset_type_uuid,
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/cylinder_report/{user_uuid}", response_class=ORJSONResponse)
@inject
async def generate_gas_cylinder_report_handler(
    user_uuid: str,
    cylinder_uuid: str = None,
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
                    report_service.generate_gas_cylinder_report(
                        user_uuid=user.get("uuid"),
                        start_date=start_date,
                        end_date=end_date,
                        cylinder_uuid=cylinder_uuid,
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    report_service.generate_gas_cylinder_report(
                        business_uuid=user.get("business_profile").uuid,
                        start_date=start_date,
                        end_date=end_date,
                        cylinder_uuid=cylinder_uuid,
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/violations_reminders/{user_uuid}", response_class=ORJSONResponse)
@inject
async def generate_violation_reminders_report_handler(
    user_uuid: str,
    asset_uuid: str = None,
    asset_type_uuid: str = None,
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
                    report_service.generate_violation_reminder_report(
                        user_uuid=user.get("uuid"),
                        start_date=start_date,
                        end_date=end_date,
                        asset_uuid=asset_uuid,
                        asset_type_uuid=asset_type_uuid,
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    report_service.generate_violation_reminder_report(
                        business_uuid=user.get("business_profile").uuid,
                        start_date=start_date,
                        end_date=end_date,
                        asset_uuid=asset_uuid,
                        asset_type_uuid=asset_type_uuid,
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/smart_report", response_class=ORJSONResponse)
@inject
async def create_smart_report_handler(
    smart_report_payload: SmartReportPayload,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(str(smart_report_payload.user_uuid))
        if user:
            if user.get("account_type") == AccountType.INDIVIDUAL:
                smart_report_input = SmartReportInput(
                    title=smart_report_payload.title,
                    start_date=smart_report_payload.start_date,
                    end_date=smart_report_payload.end_date,
                    asset_group_uuids=smart_report_payload.asset_group,
                    asset_type_uuid=smart_report_payload.asset_type_uuid,
                    user_uuid=smart_report_payload.user_uuid,
                    report_types=smart_report_payload.report_type,
                )

                report = smart_report_service.add(smart_report_input)

                return report
            if user.get("account_type") == AccountType.BUSINESS:
                smart_report_input = SmartReportInput(
                    title=smart_report_payload.title,
                    start_date=smart_report_payload.start_date,
                    end_date=smart_report_payload.end_date,
                    asset_group_uuids=smart_report_payload.asset_group,
                    asset_type_uuid=smart_report_payload.asset_type_uuid,
                    user_uuid=smart_report_payload.user_uuid,
                    business_profile_uuid=user.get("business_profile").uuid,
                    report_types=smart_report_payload.report_type,
                )

                report = smart_report_service.add(smart_report_input)

                return report

        else:
            msg = f"{messages.USER_NOT_FOUND} {smart_report_payload.user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
