from fastapi import APIRouter,Depends
from fastapi.responses import ORJSONResponse
from dependency_injector.wiring import Provide, inject
from app.service.notification_service import NotificationService
from app.core.container import Container
from app.util.utils import send_data,send_internal_server_error,send_info
from app.schema.notification_schema import CreateNotificationSchema
from app.core import messages



router = APIRouter(
    prefix="/notification",
    tags=["notification"],
)

msg_prefix = "notification"


@router.post("",response_class=ORJSONResponse)
@inject
async def create_notification_handler(
    payload : CreateNotificationSchema,
    service : NotificationService = Depends(Provide[Container.notification_service]),
):
    try:
        notification = service.add(payload)
        return send_data(notification)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
    


@router.get("/{user_uuid}",response_class=ORJSONResponse)
@inject
async def get_user_notifications_handler(
    user_uuid:str,
    service : NotificationService = Depends(Provide[Container.notification_service]),
):
    try:
        notifications = service.get_user_notifications(user_uuid)
        return send_data(notifications)
    except Exception as e:
        msg = messages.GET_FAILED+ msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
    


@router.put("/{notification_uuid}",response_class=ORJSONResponse)
@inject
async def read_notification_handler(
    notification_uuid:str,
    service : NotificationService = Depends(Provide[Container.notification_service]),
):
    try:
        notification = service.read_notification(notification_uuid)
        return send_info(messages.UPDATE_SUCCESS + msg_prefix)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
    