from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.model.user import User
from app.schema.equipment_schema import EquipmentPayload
from app.service.equipment_service import EquipmentService
from app.util.utils import (
    allow_admins_only,
    send_client_side_error,
    send_data,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/equipments",
    tags=["equipments"],
)
msg_prefix = "equipment"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_paginated_equipments_handler(
    page: int = 1,
    page_size: int = 10,
    search_query: str = None,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user_with_permission("view_equipment")),
):
    try:
        result = service.get_paginated_equipments(
            page=page, page_size=page_size, search_query=search_query
        )
        return send_data(result)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/get_equipment_by_asset_type/{asset_type_uuid}", response_class=ORJSONResponse
)
@inject
async def get_all_equipments_by_asset_type_handler(
    asset_type_uuid: str,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user_with_permission("view_equipment")),
):
    try:
        return send_data(service.get_list_by_uuid(asset_type_uuid))
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_equipment_handler(
    payload: EquipmentPayload,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user_with_permission("create_equipment")),
):
    try:
        equipment = service.add(payload)
        return send_data(equipment)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def update_equipment_handler(
    uuid: str,
    payload: EquipmentPayload,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user_with_permission("update_equipment")),
):
    try:
        equipment = service.patch_by_uuid(uuid, payload)
        if equipment is None:
            return send_client_side_error(user_msg=messages.EQUIPMENT_NOT_FOUND + uuid)
        return send_data(equipment)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


# @router.delete(
#     "/{uuid}", dependencies=[allow_admins_only], response_class=ORJSONResponse
# )
# @inject
# async def delete_equipment_handler(
#     uuid: str,
#     service: EquipmentService = Depends(Provide[Container.equipment_service]),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         service.remove_by_uuid(uuid)
#         return send_info(messages.DELETE_SUCCESS + msg_prefix)
#     except NotFoundError as e:
#         return send_client_side_error(
#             user_msg=messages.EQUIPMENT_NOT_FOUND + str(e.detail)
#         )
#     except Exception as e:
#         msg = messages.DELETE_FAILED + msg_prefix
#         return send_internal_server_error(user_msg=msg, error=e)
