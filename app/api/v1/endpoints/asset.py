import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.asset_schema import Asset as AssetSchema
from app.schema.asset_schema import AssetCreate
from app.service.asset_service import AssetService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_handler(
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get assets")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_handler(
    asset: AssetCreate,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.create_asset(asset))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create asset")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_handler(
    uuid: str,
    updated_asset: AssetSchema,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_asset))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update asset")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_handler(
    uuid: str,
    service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Asset deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete asset")
