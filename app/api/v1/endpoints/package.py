from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import exc

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.package_schema import PackageItemAssignmentPayload, PackagePayload
from app.service.package_service import PackageService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/packages",
    tags=["packages"],
)
msg_prefix = "package"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_packages_handler(
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_packages())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_package_handler(
    payload: PackagePayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        package = service.add(payload)
        return send_data(package)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_package_handler(
    uuid: str,
    payload: PackagePayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        package = service.patch_by_uuid(uuid, payload)
        if package is None:
            return send_client_side_error(user_msg=messages.PACKAGE_NOT_FOUND + uuid)
        return send_data(package)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_package_by_uuid_handler(
    uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        package = service.get_by_uuid(uuid)
        if package is None:
            return send_client_side_error(user_msg=messages.PACKAGE_NOT_FOUND + uuid)
        return send_data(package)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_package_by_uuid_handler(
    uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PACKAGE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/package_assignment", response_class=ORJSONResponse)
@inject
async def assign_package_handler(
    payload: PackageItemAssignmentPayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.assign_package_item(payload)
        return send_info(messages.PACKAGE_ITEM_ASSIGNED_SUCCESS)
    except exc.IntegrityError as e:
        return send_client_side_error(
            user_msg=messages.PACKAGE_ITEM_NOT_FOUND + str(payload.package_item_uuids),
            dev_msg=str(e),
        )
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PACKAGE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = f"Failed to assign package item(s) to package : {payload.package_uuid}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete(
    "/package_assignment/{package_uuid}/{package_item_uuid}",
    response_class=ORJSONResponse,
)
@inject
async def delete_package_item_from_package_handler(
    package_uuid: str,
    package_item_uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        package_item = service.delete_package_item(package_uuid, package_item_uuid)
        if package_item is None:
            return send_client_side_error(
                user_msg=messages.PACKAGE_ITEM_NOT_FOUND + package_item_uuid
            )
        return send_info("Package item deleted successfully")
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.PACKAGE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
