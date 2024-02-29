from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.constants import SPEED_UNIT
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.asset_schema import AssetPayload, AssignDeviceInputPayload
from app.service.asset_service import AssetService
from app.service.tracking_event_service import TrackingEventService
from app.util.utils import (
    get_status,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
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
        asset = service.assign_device_imei(asset_uuid, payload.device_imei)
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

        latest_tracking_event = service.get_latest_tracking_event_by_device_imei(
            asset.device_imei
        )

        if latest_tracking_event is None:
            return send_info(info=messages.NO_DATA)

        distance_travelled = service.get_distance_travelled_by_device_imei(
            device_imei=asset.device_imei, date=datetime.now().strftime("%d/%m/%Y")
        )

        data = {
            "status": get_status(latest_tracking_event.event_type),
            "current_location": {
                "latitude": latest_tracking_event.latitude,
                "longitude": latest_tracking_event.longitude,
            },
            "current_speed": f"{latest_tracking_event.speed}{SPEED_UNIT}",
            "fuel_level": "N/A",
            "distance_covered_today": distance_travelled,
            "incidents": "N/A",
        }
        return send_data(data)
    except Exception as e:
        msg = messages.GET_FAILED + "device analytics"
        return send_internal_server_error(user_msg=msg, error=e)
