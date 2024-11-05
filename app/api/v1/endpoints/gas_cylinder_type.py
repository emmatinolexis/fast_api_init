from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.gas_cylinder_schema import (
    CreateGasCylinderType,
    CreateOtherCylinderType,
    UpdateGasCylinderType,
)
from app.service.gas_cylinder_type_service import GasCylinderTypeService
from app.service.other_cylinder_type_service import OtherCylinderTypeService
from app.util.enums import ActiveStatus
from app.util.utils import (
    send_client_side_error,
    send_data_with_info,
    send_internal_server_error,
)
from typing import Optional

router = APIRouter(
    prefix="/gas_cylinder_type",
    tags=["Gas Cylinder Type"],
)

msg_prefix = "gas cylinder"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_gas_cylinder_types_handler(
    status: Optional[ActiveStatus] = Query(
        None,
        description='Filter by active status'
    ), 
    search_query: str = Query(None, description="Search by cylinder name"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Page size", ge=1),
    service: GasCylinderTypeService = Depends(
        Provide[Container.gas_cylinder_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        data = service.filter_by_status_and_name(
            status=status, search_query=search_query, page=page, page_size=page_size
        )
        return send_data_with_info(data, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.GET_FAILED + f" {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_gas_cylinder_type_handler(
    payload: CreateGasCylinderType,
    service: GasCylinderTypeService = Depends(
        Provide[Container.gas_cylinder_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data_with_info(service.add(payload), messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.CREATE_FAILED + f"{msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{cylinder_type_uuid}", response_class=ORJSONResponse)
@inject
async def update_gas_cylinder_type_handler(
    cylinder_type_uuid: str,
    payload: UpdateGasCylinderType,
    service: GasCylinderTypeService = Depends(
        Provide[Container.gas_cylinder_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        cylinder_type = service.get_by_uuid(cylinder_type_uuid)
        if not cylinder_type:
            return send_client_side_error(
                user_msg=messages.GAS_CYLINDER_TYPE_NOT_FOUND + cylinder_type_uuid
            )
        return send_data_with_info(
            service.patch(cylinder_type.id, payload), messages.SUCCESS_MESSAGE
        )
    except Exception as e:
        msg = messages.UPDATE_FAILED + f"{msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_other_gas_cylinder_type_handler(
    user_uuid: str,
    payload: CreateOtherCylinderType,
    service: OtherCylinderTypeService = Depends(
        Provide[Container.other_cylinder_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        created_cylinder_type = service.create_other_gas_cylinder_type(
            user_uuid, payload
        )
        return send_data_with_info(created_cylinder_type, messages.SUCCESS_MESSAGE)
    except NotFoundError as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))
    except Exception as e:
        msg = messages.CREATE_FAILED
        return send_internal_server_error(user_msg=msg, error=e)
