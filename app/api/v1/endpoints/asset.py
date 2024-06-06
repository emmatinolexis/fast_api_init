from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.constants import ENGINE_SHUTDOWN_PASSWORD, ENGINE_SHUTDOWN_USERNAME
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.asset_schema import (
    AssetDeviceRequest,
    AssetPayload,
    AssignDeviceInputPayload,
    EngineOnPayload,
    ImmobilizerPayload,
    TheftIncidencePayload,
    TheftReportPayload,
    ThirdPartyAssetPayload,
)
from app.service.asset_device_request_service import AssetDeviceRequestService
from app.service.asset_service import AssetService
from app.service.theft_report_service import TheftReportService
from app.service.tracking_event_service import TrackingEventService
from app.util.enums import ImmobilizerReason, IncidentStatus, IncidentType
from app.util.sms import send_sms
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)
msg_prefix = "asset"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_handler(
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_asset_by_user_uuid_handler(
    user_uuid: str,
    asset_type_uuid: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        assets = service.get_assets_by_user_uuid(
            user_uuid, asset_type_uuid, page, page_size
        )

        return send_data(assets)

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_handler(
    payload: AssetPayload,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = service.create_asset(payload)
        return send_data(asset)
    except NotFoundError as e:
        return send_client_side_error(str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/stolen/assets", response_class=ORJSONResponse)
@inject
async def get_stolen_assets_handler(
    asset_type_uuid: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        assets = service.get_third_stolen_assets(asset_type_uuid, page, page_size)

        return send_data(assets)

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/third_party_asset/assets", response_class=ORJSONResponse)
@inject
async def get_third_party_assets_handler(
    asset_type_uuid: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        assets = service.get_third_party_assets(asset_type_uuid, page, page_size)

        return send_data(assets)

    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/third_party_asset", response_class=ORJSONResponse)
@inject
async def create_third_party_asset_handler(
    payload: ThirdPartyAssetPayload,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = service.create_third_party_asset(payload)
        return send_data(asset)
    except NotFoundError as e:
        return send_client_side_error(str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_handler(
    uuid: str,
    payload: AssetPayload,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = service.patch_by_uuid(uuid, payload)
        if asset is None:
            return send_client_side_error(user_msg=messages.ASSET_NOT_FOUND + uuid)
        return send_data(asset)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_handler(
    uuid: str,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.ASSET_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/{asset_uuid}", response_class=ORJSONResponse)
@inject
async def assign_device_to_asset(
    asset_uuid: str,
    payload: AssignDeviceInputPayload,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = service.assign_device_imei(asset_uuid, payload)
        return send_data(asset)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{asset_uuid}/device/analytics", response_class=ORJSONResponse)
@inject
async def get_device_analytics(
    asset_uuid: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = asset_service.get_by_uuid(asset_uuid)

        if asset is None:
            return send_client_side_error(
                user_msg=messages.ASSET_NOT_FOUND + asset_uuid
            )

        data = service.get_device_analytics(
            asset.device_imei, datetime.now().strftime("%d/%m/%Y")
        )

        if data is None:
            return send_info(info=messages.NO_DATA)

        return send_data(data)
    except Exception as e:
        msg = messages.GET_FAILED + "device analytics"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/device/requests/{user_uuid}", response_class=ORJSONResponse)
@inject
async def request_asset_device(
    user_uuid: str,
    payload: AssetDeviceRequest,
    request_service: AssetDeviceRequestService = Depends(
        Provide[Container.asset_device_request_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        request_service.create_asset_device_request(
            user_uuid=user_uuid, payload=payload
        )

        return send_info(info=messages.ASSET_DEVICE_REQUEST_CREATED)
    except Exception as e:
        msg = messages.CREATE_FAILED + f"{msg_prefix} device request"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/device/requests/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_asset_device_requests_by_user(
    user_uuid: str,
    request_service: AssetDeviceRequestService = Depends(
        Provide[Container.asset_device_request_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        requests = request_service.get_asset_device_requests_by_user_uuid(user_uuid)

        return send_data(requests)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/device/requests", response_class=ORJSONResponse)
@inject
async def get_asset_device_requests(
    request_service: AssetDeviceRequestService = Depends(
        Provide[Container.asset_device_request_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        requests = request_service.get_asset_device_requests()
        return send_data(requests)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/process-device-request/{request_uuid}", response_class=ORJSONResponse)
@inject
async def update_status_request(
    request_uuid: str,
    request_service: AssetDeviceRequestService = Depends(
        Provide[Container.asset_device_request_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        request_service.update_status(request_uuid)
        msg = "Status Updated successfully"
        return send_info(msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/immobilize/off", response_class=ORJSONResponse)
@inject
async def shutdown_engine_request_handler(
    shutdown_payload: ImmobilizerPayload,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        request = asset_service.shutdown_engine(shutdown_payload.asset_uuid)
        if request.manufacturer.shutdown_on_command and request.sim_phone_number:
            shutdown_message = (
                f"{ENGINE_SHUTDOWN_USERNAME} "
                f"{ENGINE_SHUTDOWN_PASSWORD} "
                f"{request.manufacturer.shutdown_on_command.get('queued_shutdown_command')}"
            )

            sms_response = await send_sms(
                f"{request.sim_phone_number}", f"{shutdown_message}"
            )

            if sms_response:
                asset_service.report_immobilizer_activity(shutdown_payload)
                if shutdown_payload.reason == ImmobilizerReason.STOLEN:
                    incident_payload = TheftIncidencePayload(
                        asset_uuid=shutdown_payload.asset_uuid,
                        user_uuid=current_user.uuid,
                        incident_type=IncidentType.THEFT,
                        status=IncidentStatus.UNRESOLVED,
                    )
                    theft_incident = asset_service.report_theft_activity(
                        incident_payload
                    )

                    incident_report_payload = TheftReportPayload(
                        title=f"{current_user.first_name} {current_user.last_name} reported an incidence",
                        report_details=f"Asset theft incident reported for {request.asset.asset_name}",
                        user_uuid=current_user.uuid,
                        theft_incident_uuid=theft_incident.uuid,
                    )

                    asset_service.create_initial_incident_report(
                        incident_report_payload
                    )
                    asset_service.update_asset_stolen_status_to_true(
                        shutdown_payload.asset_uuid
                    )

                return send_info("Engine shutdown initiated successfully")
            else:
                msg = f"Failed to send SMS to {request.sim_phone_number}"
                return send_internal_server_error(user_msg=msg, error=msg)

        msg = f"Device shutdown command not set for {request.manufacturer.manufacturer_name} or invalid phone number"
        return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/immobilize/on", response_class=ORJSONResponse)
@inject
async def on_engine_request_handler(
    engine_on_payload: EngineOnPayload,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        request = asset_service.shutdown_engine(engine_on_payload.asset_uuid)
        if request.manufacturer.shutdown_on_command and request.sim_phone_number:
            engine_on_message = (
                f"{ENGINE_SHUTDOWN_USERNAME} "
                f"{ENGINE_SHUTDOWN_PASSWORD} "
                f"{request.manufacturer.shutdown_on_command.get('queued_on_command')}"
            )

            sms_response = await send_sms(
                f"{request.sim_phone_number}", f"{engine_on_message}"
            )

            if sms_response:
                asset_service.report_immobilizer_activity(engine_on_payload)
                return send_info("Engine on initiated successfully")
            else:
                msg = f"Failed to send SMS to {request.sim_phone_number}"
                return send_internal_server_error(user_msg=msg, error=msg)

        msg = f"Device engine on command not set for {request.manufacturer.manufacturer_name} or invalid phone number"
        return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{asset_uuid}/last_immobilizer_action", response_class=ORJSONResponse)
@inject
async def get_last_immobilizer_action(
    asset_uuid: str,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        action = asset_service.get_last_immobilizer_action(asset_uuid)
        return send_data(action)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} device requests"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/immobilizer/theft_incidence", response_class=ORJSONResponse)
@inject
async def get_all_incidence_handler(
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        incidence = asset_service.get_all_theft_incidence()
        return send_data(incidence)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} theft incidence"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/theft_incidence/{incident_uuid}/resolve", response_class=ORJSONResponse)
@inject
async def mark_incident_as_resolved_handler(
    incident_uuid: str,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        incident = asset_service.mark_as_resolved(incident_uuid)
        asset_service.update_asset_stolen_status_to_false(incident.asset_uuid)
        msg = "Successfully marked as resolved"
        return send_info(msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} theft incidence"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/theft_reports/{incident_uuid}", response_class=ORJSONResponse)
@inject
async def get_incident_reports_handler(
    incident_uuid: str,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        reports = asset_service.get_incident_reports(incident_uuid)
        return send_data(reports)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} theft incidence"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/theft_reports/create", response_class=ORJSONResponse)
@inject
async def create_theft_report_handler(
    payload: TheftReportPayload,
    theft_report_service: TheftReportService = Depends(
        Provide[Container.theft_report_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        reports = theft_report_service.add(payload)
        return send_data(reports)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix} theft report"
        return send_internal_server_error(user_msg=msg, error=e)
