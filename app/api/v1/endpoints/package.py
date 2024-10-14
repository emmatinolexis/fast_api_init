from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import exc

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.package_schema import (
    PackageItemAssignmentPayload,
    PaystackPackagePlanPayload,
)
from app.service.package_service import PackageService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
    allow_admins_only
)

router = APIRouter(
    prefix="/packages",
    tags=["packages"],
)
msg_prefix = "package"


@router.get("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_packages_handler(
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("view_package")),
):
    try:
        return send_data(service.get_all_paystack_plans())
    except Exception as e:
        msg = f"{messages.GET_FAILED}{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_package_handler(
    payload: PaystackPackagePlanPayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("create_package")),
):
    try:
        package = service.create_paystack_package_plan(payload)
        return send_data(package)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{plan_code}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_package_handler(
    plan_code: str,
    payload: PaystackPackagePlanPayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("update_package")),
):
    try:
        package = service.update_paystack_plan(plan_code, payload)
        if package is None:
            return send_client_side_error(
                user_msg=messages.PACKAGE_NOT_FOUND + plan_code
            )
        return send_info(package)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{plan_code}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_package_by_uuid_handler(
    plan_code: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("view_package")),
):
    try:
        package = service.get_paystack_plan(plan_code)
        if package is None:
            return send_client_side_error(
                user_msg=messages.PACKAGE_NOT_FOUND + plan_code
            )
        return send_data(package)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


# @router.delete("/{uuid}", response_class=ORJSONResponse)
# @inject
# async def delete_package_by_uuid_handler(
#     uuid: str,
#     service: PackageService = Depends(Provide[Container.package_service]),
#     current_user: User = Depends(get_current_user_with_permission("create_package")),
# ):
#     try:
#         service.remove_by_uuid(uuid)
#         return send_info(messages.DELETE_SUCCESS + msg_prefix)
#     except NotFoundError as e:
#         return send_client_side_error(
#             user_msg=messages.PACKAGE_NOT_FOUND + str(e.detail)
#         )
#     except Exception as e:
#         msg = messages.DELETE_FAILED + msg_prefix
#         return send_internal_server_error(user_msg=msg, error=e)


@router.post("/package_assignment", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def assign_package_handler(
    payload: PackageItemAssignmentPayload,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("create_package")),
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
        msg = (
            f"Failed to assign package item(s) to package : {payload.package_plan_code}"
        )
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete(
    "/package_assignment/{plan_code}/{package_item_uuid}",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def delete_package_item_from_package_handler(
    plan_code: str,
    package_item_uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user_with_permission("update_package")),
):
    try:
        package_item = service.delete_package_item(plan_code, package_item_uuid)
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
