import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.asset_schema import AssetLocation
from app.service.asset_location_service import AssetLocationService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/asset_locations",
    tags=["asset locations"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_location_handler(
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get asset locations")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_location_handler(
    asset_location: AssetLocation,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(asset_location))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create asset location")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_location_handler(
    uuid: str,
    updated_asset_location: AssetLocation,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_asset_location))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update asset location")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_location_handler(
    uuid: str,
    service: AssetLocationService = Depends(Provide[Container.asset_location_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Asset type deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete asset location")
