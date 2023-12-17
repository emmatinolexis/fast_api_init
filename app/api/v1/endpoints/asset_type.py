from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.asset_schema import AssetTypePayload
from app.service.asset_type_service import AssetTypeService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/asset_types",
    tags=["asset types"],
)
msg_prefix = "asset type"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_type_handler(
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_type_handler(
    payload: AssetTypePayload,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset_type = send_data(service.add(payload))
        return asset_type
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_type_handler(
    uuid: str,
    payload: AssetTypePayload,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset_type = service.patch_by_uuid(uuid, payload)
        if asset_type is None:
            return send_client_side_error(user_msg=messages.ASSET_TYPE_NOT_FOUND + uuid)
        return send_data(asset_type)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_type_handler(
    uuid: str,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.ASSET_TYPE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
