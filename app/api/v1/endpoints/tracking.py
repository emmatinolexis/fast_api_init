from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
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
    limit: int = 100,
):
    try:
        events = service.get_events_by_device_imei(device_imei, date, limit)
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
    limit: int = 100,
):
    try:
        events = service.get_events_by_user(user_uuid, date, limit)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA_FOUND)
        return send_data(events)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/route_replay/{device_imei}", response_class=ORJSONResponse)
@inject
async def get_route_replay_tracking_details_handler(
    device_imei: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
    limit: int = 100,
):
    try:
        events = service.get_route_replay_events_by_device_imei(
            device_imei, date, limit
        )
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA_FOUND)
        return send_data(events)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
