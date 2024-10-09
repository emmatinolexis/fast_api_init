from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.model.user import User
from app.schema.permission_schema import RolePayload
from app.service.permission_service import PermissionService
from app.service.role_service import RoleService
from app.util.enums import RoleType
from app.util.utils import send_data, send_data_with_info, send_internal_server_error

router = APIRouter(
    prefix="/permissions",
    tags=["Roles and permissions"],
)
msg_prefix = "permission"


@router.post("/synchronize/", response_class=ORJSONResponse)
@inject
async def synchronize_permissions_handler(
    service: PermissionService = Depends(Provide[Container.permission_service]),
    current_user: User = Depends(
        get_current_user_with_permission("synchronize_permissions")
    ),
):
    try:
        permissions = service.synchronize_permissions()
        return send_data(permissions)
    except Exception as e:
        msg = messages.FAILED_TO_CREATE + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_permission_handler(
    service: PermissionService = Depends(Provide[Container.permission_service]),
    current_user: User = Depends(get_current_user_with_permission("view_permissions")),
):
    try:
        permissions = service.get_permissions()
        return send_data_with_info(permissions, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/roles", response_class=ORJSONResponse)
@inject
async def get_all_roles_handler(
    role_type: RoleType = None,
    service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user_with_permission("view_roles")),
):
    try:
        return send_data(service.get_all_roles(role_type))
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/roles", response_class=ORJSONResponse)
@inject
async def create_role_handler(
    payload: RolePayload,
    service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user_with_permission("create_role")),
):
    try:
        role = service.create_role_permission(payload)
        return send_data_with_info(role, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/roles/{role_uuid}", response_class=ORJSONResponse)
@inject
async def update_role_handler(
    payload: RolePayload,
    role_uuid: str,
    service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
):
    try:
        role = service.get_by_uuid(role_uuid)
        if role:
            update_role = service.update_role(payload, role_uuid)
            return send_data_with_info(update_role, messages.SUCCESS_MESSAGE)
        msg = "role not found"
        return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/role/{role_uuid}", response_class=ORJSONResponse)
@inject
async def get_role_handler(
    role_uuid: str,
    service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user_with_permission("view_roles")),
):
    try:
        role = service.get_role(role_uuid)
        return send_data(role)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
