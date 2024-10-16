from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.package_schema import PackageItemPayload
from app.service.package_item_service import PackageItemService
from app.util.utils import (
    allow_admins_only,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/package_items",
    tags=["package items"],
)
msg_prefix = "package item"


@router.get("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_package_items_handler(
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user_with_permission("view_package")),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_package_item_handler(
    payload: PackageItemPayload,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user_with_permission("create_package")),
):
    try:
        package_item = service.add(payload)
        return send_data(package_item)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_package_item_handler(
    uuid: str,
    payload: PackageItemPayload,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user_with_permission("update_package")),
):
    try:
        package_item = service.patch_by_uuid(uuid, payload)
        if package_item is None:
            return send_client_side_error(
                user_msg=messages.PACKAGE_ITEM_NOT_FOUND + uuid
            )
        return send_data(package_item)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete(
    "/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse
)
@inject
async def delete_package_item_handler(
    uuid: str,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(
        get_current_user_with_permission("delete_package_item")
    ),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PACKAGE_ITEM_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
