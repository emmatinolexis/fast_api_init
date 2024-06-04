from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.fine_report_schema import FineReportPayload
from app.service.fine_report_service import FineReportService
from app.util.utils import (send_client_side_error, send_data,
                            send_internal_server_error)

router = APIRouter(
    prefix="/fine_reports",
    tags=["Fine Reports"],
)
msg_prefix = "fine_reports"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_fine_report_handler(
    service: FineReportService = Depends(Provide[Container.fine_report_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_fine_reports())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_fine_report_handler(
    payload: FineReportPayload,
    service: FineReportService = Depends(Provide[Container.fine_report_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        fine_report = service.add(payload)
        return send_data(fine_report)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_fine_report_handler(
    uuid: str,
    payload: FineReportPayload,
    service: FineReportService = Depends(Provide[Container.fine_report_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        fine_report = service.patch_by_uuid(uuid, payload)
        if fine_report is None:
            return send_client_side_error(
                user_msg=messages.FINE_REPORT_NOT_FOUND + uuid
            )
        return send_data(fine_report)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_fine_report_by_uuid_handler(
    uuid: str,
    service: FineReportService = Depends(Provide[Container.fine_report_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        fine_report = service.get_fine_report(uuid)
        if fine_report is None:
            return send_client_side_error(
                user_msg=messages.FINE_REPORT_NOT_FOUND + uuid
            )
        return send_data(fine_report)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
