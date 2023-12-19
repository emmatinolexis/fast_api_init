import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.equipment_schema import EquipmentTypePayload
from app.service.equipment_type_service import EquipmentTypeService
from app.util.utils import (
    allow_admins_only,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/equipment_types",
    tags=["equipment types"],
)
log = structlog.get_logger()
msg_prefix = "equipment type"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_equipment_types_handler(
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_equipment_type_handler(
    payload: EquipmentTypePayload,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        equipment_type = service.create_equipment_type(payload)
        return send_data(equipment_type)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.EQUIPMENT_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_equipment_type_handler(
    uuid: str,
    payload: EquipmentTypePayload,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        equipment_type = service.update_equipment_type(uuid, payload)
        if equipment_type is None:
            return send_client_side_error(
                user_msg=messages.EQUIPMENT_TYPE_NOT_FOUND + uuid
            )
        return send_data(equipment_type)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.EQUIPMENT_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete(
    "/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse
)
@inject
async def delete_equipment_type_handler(
    uuid: str,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.EQUIPMENT_TYPE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
