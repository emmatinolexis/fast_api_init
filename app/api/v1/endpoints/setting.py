from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.setting_schema import SettingPayload
from app.service.settings_service import SettingService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_internal_server_error,
    allow_admins_only,
)

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)
msg_prefix = "settings"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_settings_handler(
    service: SettingService = Depends(Provide[Container.setting_service]),
):
    try:
        return send_data(await service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_setting_handler(
    uuid: str,
    payload: SettingPayload,
    service: SettingService = Depends(Provide[Container.setting_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        setting = await service.patch_by_uuid(uuid, payload)
        if setting is None:
            return send_client_side_error(user_msg="Settings not found")
        return send_data_with_info(setting, "Settings updated successfully")
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
