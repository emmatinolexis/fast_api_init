from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.device_schema import InventoryPayload, InventoryUpdatePayload
from app.service.inventory_service import InventoryService
from app.util.utils import send_client_side_error, send_data, send_internal_server_error

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)
msg_prefix = "inventory"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_inventory_handler(
    page: int = Query(1, ge=1, description="Page number, default is 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    search_query: str = Query(
        None, description="Search by device name or manufacturer name"
    ),
    service: InventoryService = Depends(Provide[Container.inventory_service]),
):
    try:
        inventories = service.get_all_inventory(
            page=page, page_size=page_size, search_query=search_query
        )
        return send_data(inventories)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)

@router.get("/{uuid}",response_class=ORJSONResponse)
@inject
async def get_inventory_by_uuid(
    uuid: UUID,
    service: InventoryService = Depends(Provide[Container.inventory_service]),
    current_user: User = Depends(get_current_user)
):
    try:
        inventory = service.get_inventory_by_uuid(uuid)
        return send_data(inventory)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.GET_FAILED+ "inventory"
        )
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_device_handler(
    payload: InventoryPayload,
    service: InventoryService = Depends(Provide[Container.inventory_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        devices = service.create_inventory(payload)
        return send_data(devices)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{inventory_uuid}", response_class=ORJSONResponse)
@inject
async def update_inventory_handler(
    inventory_uuid: UUID,
    payload: InventoryUpdatePayload,
    service: InventoryService = Depends(Provide[Container.inventory_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_inventory = service.update_inventory(inventory_uuid, payload)
        return send_data(updated_inventory)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DEVICE_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
