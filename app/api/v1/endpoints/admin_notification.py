from fastapi import APIRouter,Depends
from dependency_injector.wiring import Provide, inject
from app.service.admin_notification_service import  AdminNotificationService
from app.core.container import Container
from app.model.user import User
from app.core.dependencies import get_current_user
from app.core.exceptions import UnAuthorizedError
from app.util.utils import send_info,send_data,send_client_side_error,send_internal_server_error
from app.core import messages





router = APIRouter(
    prefix="/admin/notifications",
    tags=["admin_notifications"],
)

msg_prefix =  "Admin Notification"


@router.get("/")
@inject
async def get_notifications(
    service: AdminNotificationService = Depends(Provide[Container.admin_notification_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        notifications  = service.get_admin_notifications(current_user.uuid,current_user.user_role.role_name.strip())
        return send_data(notifications)
    except UnAuthorizedError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg,error=str(e))

        
