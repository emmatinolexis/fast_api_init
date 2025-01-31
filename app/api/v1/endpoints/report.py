import json
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user, get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.core.settings import settings
from app.model.user import User
from app.schema.report_schema import (
    SmartReportInput,
    SmartReportPayload,
    SmartReportSharePayload,
)
from app.service.asset_service import AssetService
from app.service.device_events_service import DeviceEventService
from app.service.gas_cylinder_event_service import GasCylinderEventService
from app.service.smart_report_service import SmartReportService
from app.service.user_service import UserService
from app.util.email import send_smart_report_email
from app.util.enums import EmailPurpose, FileFormat, SmartReportStatus
from app.util.utils import (
    get_content_type,
    send_client_side_error,
    send_data_with_info,
    send_info,
    send_internal_server_error,
    upload_to_s3,
)

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
    current_user: User = Depends(
        get_current_user_with_permission("distance_traveled_report")
    ),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)
        if user:
            return send_data_with_info(
                report_service.generate_distance_speed_report(
                    business_uuid=user.get("business_profile").uuid,
                    start_date=start_date,
                    end_date=end_date,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                messages.SUCCESS_MESSAGE,
            )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_client_side_error(user_msg=msg, dev_msg=msg)
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
            return send_data_with_info(
                report_service.generate_violation_reminder_report(
                    business_uuid=user.get("business_profile").uuid,
                    start_date=start_date,
                    end_date=end_date,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                messages.SUCCESS_MESSAGE,
            )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_client_side_error(user_msg=msg, dev_msg=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/smart_report", response_class=ORJSONResponse)
@inject
async def create_smart_report_handler(
    smart_report_payload: SmartReportPayload,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(str(smart_report_payload.user_uuid))

        if user:
            smart_report_input = SmartReportInput(
                title=smart_report_payload.title,
                start_date=smart_report_payload.start_date,
                end_date=smart_report_payload.end_date,
                asset_group_uuids=smart_report_payload.asset_group,
                asset_type_uuid=smart_report_payload.asset_type_uuid,
                user_uuid=smart_report_payload.user_uuid,
                business_profile_uuid=user.get("business_profile").uuid,
                report_types=smart_report_payload.report_type,
                status=SmartReportStatus.PENDING,
            )

            report = smart_report_service.add(smart_report_input)
            logging.info(f"Smart report created: {report}")
            return send_data_with_info(report, messages.SUCCESS_MESSAGE)
        else:
            msg = f"{messages.USER_NOT_FOUND} {smart_report_payload.user_uuid}"
            return send_client_side_error(user_msg=msg, dev_msg=msg)

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/smart_report/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_smart_report_by_user_handler(
    user_uuid: str,
    query_parameter: str = None,
    created_by: str = None,
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
            reports = smart_report_service.get_reports(
                business_profile_uuid=user.get("business_profile").uuid,
                query_parameter=query_parameter,
                created_by=created_by,
                page=page,
                page_size=page_size,
            )

            return send_data_with_info(reports, messages.SUCCESS_MESSAGE)
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}")
@inject
async def get_gas_report(
    user_uuid: str,
    start_date: str,
    end_date: str,
    search: str = Query(
        None, description="Search for gas cylinder by Name or Serial Number"
    ),
    service: GasCylinderEventService = Depends(
        Provide[Container.gas_cylinder_event_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)

        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND,
                dev_msg=f"User with uuid {user_uuid} not found",
            )

        return send_data_with_info(
            service.generate_report_business(
                business_uuid=user.get("business_profile").uuid,
                start_date=start_date,
                end_date=end_date,
                search=search,
            ),
            messages.SUCCESS_MESSAGE,
        )

    except Exception as e:
        return send_internal_server_error(user_msg="Failed to get gas report", error=e)


@router.get(
    "/smart_report_generate_result/generate_result", response_class=ORJSONResponse
)
@inject
async def generate_smart_report_handler(
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
):
    try:
        smart_report = smart_report_service.get_unprocessed_smart_report_by_uuid()

        if not smart_report:
            msg = "There are no smart report to process"
            return send_info(msg)
        if smart_report:
            smart_report_service.update_smart_report_status(
                smart_report.get("uuid"), SmartReportStatus.PROCESSING
            )

            report = smart_report_service.generate_smart_report(smart_report)

            if report:
                report_json = json.dumps(report, indent=4, default=str)
                file_format = FileFormat.JSON
                content_type = get_content_type(file_format)
                file_content = report_json.encode("utf-8")

                url = await upload_to_s3(
                    file_name=f"{smart_report.get('uuid')}.{file_format}",
                    file_content=file_content,
                    content_type=content_type,
                    folder_name="smart_reports",
                )
                smart_report_service.update_smart_report_status(
                    smart_report.get("uuid"), SmartReportStatus.PROCESSED, url
                )

                report_message = (
                    f"Hello {smart_report.get('created_by')},<br> "
                    f"We are pleased to inform you that your  {smart_report.get('title')} is now available."
                    f"<br> Please log in to your account to view the report. "
                    f"Click the button below to access your smart report"
                )

                await send_smart_report_email(
                    email=smart_report.get("created_by_email"),
                    message=report_message,
                    title=f"{smart_report.get('title')}",
                    btn_url=settings.SMART_REPORT_URL,
                    btn_text="View Smart Report",
                    email_purpose=EmailPurpose.SMART_REPORT_ALERT,
                )

                msg = "Smart report generated successfully"
                logging.info(msg)
                return send_info(msg)

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        logging.info(e)
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/smart_report/get/{smart_report_uuid}", response_class=ORJSONResponse)
@inject
async def get_processed_smart_report_handler(
    smart_report_uuid: str,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
):
    try:
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)
        if smart_report:
            if smart_report.status != SmartReportStatus.PROCESSED:
                msg = "Smart report not processed"
                send_client_side_error(msg)

            smart_report = smart_report_service.get_processed_smart_report(smart_report)

            return send_data_with_info(smart_report, "Report fetched successfully")

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        logging.info(e)
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/smart_report/share/{smart_report_uuid}", response_class=ORJSONResponse)
@inject
async def share_smart_report_handler(
    smart_report_share_payload: SmartReportSharePayload,
    smart_report_uuid: str,
    smart_report_service: SmartReportService = Depends(
        Provide[Container.smart_report_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        # get the smart report
        smart_report = smart_report_service.get_by_uuid(smart_report_uuid)

        # throw an error if smart report not found
        if not smart_report:
            return send_client_side_error(messages.SMART_REPORT_NOT_FOUND)

        users = []
        report_link = f"{settings.SMART_REPORT_SHARE_URL}{smart_report.uuid}"

        # get all the users to share
        for user_uuid in smart_report_share_payload.user_uuids:
            user = user_service.get_by_uuid(str(user_uuid))

            if not user:
                return send_client_side_error(
                    user_msg="User not found",
                    dev_msg=f"messages.USER_NOT_FOUND {user_uuid}",
                )

            user = {
                "email": user.email_address,
                "name": f"{user.first_name} {user.last_name}",
            }

            users.append(user)

        # send emails to recipients
        for user in users:
            report_message = (
                f"Hello {user.get('name')}, we wanted to inform you that your {smart_report.title} is now ready. "
                f"<br> Login to your account to view report"
            )

            await send_smart_report_email(
                email=user.get("email"),
                message=report_message,
                title=f"{smart_report.title}",
                btn_url=report_link,
                btn_text="View Smart Report",
                email_purpose=EmailPurpose.SMART_REPORT_ALERT,
            )

        return send_info("Smart Report Shared successfully")

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        logging.info(e)
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/cylinder_report/{cylinder_uuid}", response_class=ORJSONResponse)
@inject
async def get_cylinder_report(
    cylinder_uuid: str,
    start_date: str = Query(..., description="Start date in formats: DD/MM/YYYY, etc."),
    end_date: str = Query(..., description="End date in formats: DD/MM/YYYY, etc."),
    service: DeviceEventService = Depends(Provide[Container.device_events_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        data = service.generate_report_single_cylinder(
            cylinder_uuid=cylinder_uuid, start_date=start_date, end_date=end_date
        )
        return send_data_with_info(data, messages.GET_SUCCESS + "Cylinder Report")
    except ValueError as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.GET_FAILED + "cylinder report")
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to get cylinder report", error=e
        )
