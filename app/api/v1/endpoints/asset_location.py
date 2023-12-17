from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.asset_schema import AssetLocationPayload
from app.service.asset_location_service import AssetLocationService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/asset_locations",
    tags=["asset locations"],
)
msg_prefix = "asset location"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_location_handler(
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_location_handler(
    payload: AssetLocationPayload,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset_location = service.create_asset_location(payload)
        return send_data(asset_location)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.ASSET_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_location_handler(
    uuid: str,
    payload: AssetLocationPayload,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset_location = service.update_asset_location(uuid, payload)
        if asset_location is None:
            return send_client_side_error(
                user_msg=messages.ASSET_LOCATION_NOT_FOUND + uuid
            )
        return send_data(asset_location)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.ASSET_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_location_handler(
    uuid: str,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.ASSET_LOCATION_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
