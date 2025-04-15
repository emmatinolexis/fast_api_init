from typing import Optional
from uuid import UUID
from app.client.redis import RedisClient

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.asset_schema import AssetType, VehicleMakePayload
from app.service.vehicle_make_service import VehicleMakeService
from app.util.utils import (
    allow_admins_only,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/vehicle_make",
    tags=["vehicle make"],
)
msg_prefix = "vehicle_make"

redis = RedisClient()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_vehicle_makes_handler(
    asset_type: Optional[AssetType] = Query(
        None, description="Filter by asset type (CAR or MOTORBIKE)"
    ),
    service: VehicleMakeService = Depends(Provide[Container.vehicle_make_service]),
):
    try:
        # Create unique cache key
        cache_key = f"vehicle_makes:{asset_type}"

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        makes = await service.get_vehicle_makes(asset_type=asset_type)

        # Cache the result for 24 hours
        await redis.set_cache(cache_key, makes)

        return send_data(makes)
    except Exception as e:
        msg = messages.GET_FAILED + f" {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/{make_uuid}/models",
    response_class=ORJSONResponse,
    responses={404: {"description": "Vehicle make not found"}},
)
@inject
async def get_vehicle_models_handler(
    make_uuid: UUID = Path(..., description="UUID of the vehicle make"),
    service: VehicleMakeService = Depends(Provide[Container.vehicle_make_service]),
):
    try:
        # Create unique cache key
        cache_key = f"vehicle_models:{make_uuid}"

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        models = await service.get_vehicle_models_by_make_uuid(make_uuid)
        # Cache the result for 24 hours
        await redis.set_cache(cache_key, models)
        return send_data(models)
    except ValueError as ve:
        return send_info(str(ve), status_code=404)
    except Exception as e:
        msg = messages.GET_FAILED + f" models for {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def create_vehicle_makes_handler(
    payload: VehicleMakePayload,
    service: VehicleMakeService = Depends(Provide[Container.vehicle_make_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        await service.create_make(payload)
        await redis.delete_by_pattern("vehicle_makes:*")
        await redis.delete_by_pattern("vehicle_models:*")
        return send_info("Upload successful")
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
