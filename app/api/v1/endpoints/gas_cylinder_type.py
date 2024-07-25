from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.gas_cylinder_schema import (
    CreateGasCylinderType,
    CreateOtherCylinderType,
)
from app.service.gas_cylinder_type_service import GasCylinderTypeService
from app.service.other_cylinder_type_service import OtherCylinderTypeService
from app.service.user_service import UserService
from app.util.enums import AccountType
from app.util.utils import send_data, send_internal_server_error

router = APIRouter(
    prefix="/gas_cylinder_type",
    tags=["Gas Cylinder Type"],
)

msg_prefix = "gas cylinder"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_gas_cylinder_types_handler(
    service: GasCylinderTypeService = Depends(
        Provide[Container.gas_cylinder_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
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
        return send_data(service.add(payload))
    except Exception as e:
        msg = messages.CREATE_FAILED + f"{msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_other_gas_cylinder_type_handler(
    user_uuid: str,
    payload: CreateGasCylinderType,
    service: OtherCylinderTypeService = Depends(
        Provide[Container.other_cylinder_type_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = user_service.get_user_by_uuid(user_uuid)
        if user:
            if user.get("account_type") == AccountType.INDIVIDUAL:
                return send_data(
                    service.add(
                        CreateOtherCylinderType(
                            name=payload.name,
                            image_url=payload.image_url,
                            empty_weight=payload.empty_weight,
                            full_weight=payload.full_weight,
                            user_uuid=str(user.get("uuid")),
                        )
                    )
                )
            if user.get("account_type") == AccountType.BUSINESS:
                return send_data(
                    service.add(
                        CreateOtherCylinderType(
                            name=payload.name,
                            image_url=payload.image_url,
                            empty_weight=payload.empty_weight,
                            full_weight=payload.full_weight,
                            business_profile_uuid=str(
                                user.get("business_profile").uuid
                            ),
                            user_uuid=str(user.get("uuid")),
                        )
                    )
                )
        else:
            msg = f"{messages.USER_NOT_FOUND} {user_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
    except Exception as e:
        msg = messages.CREATE_FAILED + f"{msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)
