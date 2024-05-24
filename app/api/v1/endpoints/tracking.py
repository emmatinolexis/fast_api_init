from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.service.asset_service import AssetService
from app.service.tracking_event_service import TrackingEventService
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/tracking",
    tags=["tracking"],
)
msg_prefix = "tracking"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_tracking_details_handler(
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    device_imei: str = None,
    date: str = None,
):
    try:
        events = service.get_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA_FOUND)
        return send_data(events)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_tracking_details_by_user_handler(
    user_uuid: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
):
    try:
        events = service.get_events_by_user(user_uuid, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA_FOUND)
        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/route_replay/{device_imei}", response_class=ORJSONResponse)
@inject
async def get_route_replay_tracking_details_handler(
    device_imei: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
):
    try:
        events = service.get_route_replay_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA_FOUND)
        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/over_speeding/{asset_uuid}", response_class=ORJSONResponse)
@inject
async def get_over_speeding_stats_handler(
    asset_uuid: str,
    date_from: datetime,
    date_to: datetime,
    tracking_service: TrackingEventService = Depends(
        Provide[Container.tracking_event_service]
    ),
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = asset_service.get_by_uuid(asset_uuid)

        if asset is None:
            msg = f"{messages.ASSET_NOT_FOUND}{asset_uuid}"
            return send_client_side_error(msg)
        if asset.device_imei is None:
            msg = "Asset not linked to a device"
            return send_client_side_error(msg)
        speeding_data = tracking_service.get_asset_average_speed(
            asset.device_imei, date_from, date_to
        )
        return send_data(speeding_data)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
