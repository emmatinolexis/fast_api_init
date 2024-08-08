from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.report_schema import SmartReportInput, SmartReportPayload
from app.service.asset_service import AssetService
from app.service.smart_report_service import SmartReportService
from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import convert_date_format, send_data, send_internal_server_error

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


@router.get(
    "/smart_report/fleet_overview/{smart_report_uuid}", response_class=ORJSONResponse
)
@inject
async def view_smart_report_fleet_overview_handler(
    smart_report_uuid: str,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)

        if not smart_report:
            usr_msg = "Smart report not found"
            dev_msg = f"Smart report not found for {smart_report_uuid}"
            return send_internal_server_error(user_msg=usr_msg, error=dev_msg)

        user = user_service.get_user_by_uuid(str(smart_report.user_uuid))

        if user.get("account_type") == AccountType.INDIVIDUAL:
            report_data = smart_report_service.generate_smart_report_fleet_overview(
                convert_date_format(smart_report.start_date),
                convert_date_format(smart_report.end_date),
                smart_report.asset_type_uuid,
                smart_report.asset_group_uuids.get("asset_uuids"),
                user_uuid=smart_report.user_uuid,
            )

            return report_data

        if user.get("account_type") == AccountType.BUSINESS:
            report_data = smart_report_service.generate_smart_report_fleet_overview(
                convert_date_format(smart_report.start_date),
                convert_date_format(smart_report.end_date),
                smart_report.asset_type_uuid,
                smart_report.asset_group_uuids.get("asset_uuids"),
                business_uuid=smart_report.business_profile_uuid,
            )

            return report_data

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/smart_report/total_distance/{smart_report_uuid}", response_class=ORJSONResponse
)
@inject
async def view_smart_report_total_distance_covered_handler(
    smart_report_uuid: str,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)

        if not smart_report:
            usr_msg = "Smart report not found"
            dev_msg = f"Smart report not found for {smart_report_uuid}"
            return send_internal_server_error(user_msg=usr_msg, error=dev_msg)

        user = user_service.get_user_by_uuid(str(smart_report.user_uuid))
        if not user:
            usr_msg = "User not found"
            dev_msg = f"User not found for  {smart_report.user_uuid}"
            return send_internal_server_error(user_msg=usr_msg, error=dev_msg)

        report_data = smart_report_service.generate_total_distance_report(
            convert_date_format(smart_report.start_date),
            convert_date_format(smart_report.end_date),
            smart_report.asset_group_uuids.get("asset_uuids"),
        )

        return report_data

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/smart_report/fleet_performance/{smart_report_uuid}", response_class=ORJSONResponse
)
@inject
async def view_smart_report_fleet_performance_handler(
    smart_report_uuid: str,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)

        if not smart_report:
            usr_msg = "Smart report not found"
            dev_msg = f"Smart report not found for {smart_report_uuid}"
            return send_internal_server_error(user_msg=usr_msg, error=dev_msg)

        violations = smart_report_service.generate_violation_report(
            convert_date_format(smart_report.start_date),
            convert_date_format(smart_report.end_date),
            smart_report.asset_group_uuids.get("asset_uuids"),
        )
        return violations
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/smart_report/cost_analysis/{smart_report_uuid}", response_class=ORJSONResponse
)
@inject
async def view_smart_report_cost_analysis_handler(
    smart_report_uuid: str,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return {
            "fuel_cost": {
                "January": 550,
                "February": 230,
                "March": 129,
                "April": 110,
                "May": 350,
                "June": 65,
                "July": 180,
                "Aug": 360,
                "Sept": 320,
                "Oct": 120,
                "Nov": 130,
                "Dec": 160,
            },
            "total_fuel": 2890,
            "fuel_cost_by_asset_type": {
                "trucks": 0,
                "cars": 0,
                "bulldozers": 0,
                "cranes": 0,
            },
            "fuel_cost_by_asset_type_in_percentage": {
                "trucks": 20,
                "cars": 30,
                "bulldozers": 30,
                "cranes": 80,
            },
        }
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/smart_report/violations/{smart_report_uuid}", response_class=ORJSONResponse
)
@inject
async def view_smart_report_violations_handler(
    smart_report_uuid: str,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)

        if not smart_report:
            usr_msg = "Smart report not found"
            dev_msg = f"Smart report not found for {smart_report_uuid}"
            return send_internal_server_error(user_msg=usr_msg, error=dev_msg)

        violations = smart_report_service.generate_violation_report(
            convert_date_format(smart_report.start_date),
            convert_date_format(smart_report.end_date),
            smart_report.asset_group_uuids.get("asset_uuids"),
            smart_report.asset_type_uuid,
        )
        return violations
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/smart_report/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_smart_report_by_user_handler(
    user_uuid: str,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(str(user_uuid))
        if user:
            if user.get("account_type") == AccountType.INDIVIDUAL:
                reports = smart_report_service.get_reports(
                    user_uuid=user_uuid, page=page, page_size=page_size
                )
                return reports

            if user.get("account_type") == AccountType.BUSINESS:
                reports = smart_report_service.get_reports(
                    business_profile_uuid=user.get("business_profile").uuid,
                    page=10,
                    page_size=page_size,
                )

                return reports

        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
