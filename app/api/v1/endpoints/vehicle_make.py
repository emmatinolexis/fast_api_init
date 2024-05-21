from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.asset_schema import VehicleMakePayload
from app.service.vehicle_make_service import VehicleMakeService
from app.util.utils import send_data, send_info, send_internal_server_error

router = APIRouter(
    prefix="/vehicle_make",
    tags=["vehicle make"],
)
msg_prefix = "vehicle_make"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_vehicle_makes_handler(
    service: VehicleMakeService = Depends(Provide[Container.vehicle_make_service]),
):
    try:
        return send_data(service.get_vehicle_makes())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_feature_handler(
    payload: VehicleMakePayload,
    service: VehicleMakeService = Depends(Provide[Container.vehicle_make_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.create_makes(payload)
        return send_info("Upload successful")
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
