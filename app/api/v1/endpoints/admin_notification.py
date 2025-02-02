from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import UnAuthorizedError
from app.model.user import User
from app.service.admin_notification_service import AdminNotificationService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/admin/notifications",
    tags=["admin_notifications"],
)

msg_prefix = "Admin Notification"


@router.get("/")
@inject
async def get_notifications(
    service: AdminNotificationService = Depends(
        Provide[Container.admin_notification_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        notifications = await service.get_admin_notifications(
            current_user.uuid, current_user.user_role.role_name.strip()
        )
        return send_data(notifications)
    except UnAuthorizedError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.put("/clear")
@inject
async def clear_notifications(
    service: AdminNotificationService = Depends(
        Provide[Container.admin_notification_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = await service.clear_notifications(str(current_user.uuid))
        return send_info(response)
    except UnAuthorizedError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.put("/{notification_uuid}")
@inject
async def read_notification(
    notification_uuid: str,
    service: AdminNotificationService = Depends(
        Provide[Container.admin_notification_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = await service.read_notification(
            notification_uuid, current_user.uuid
        )
        return send_info(messages.UPDATE_SUCCESS + msg_prefix)
    except UnAuthorizedError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))
