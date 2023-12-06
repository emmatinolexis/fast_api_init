import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.asset_schema import AssetType, AssetTypeCreate
from app.service.asset_type_service import AssetTypeService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/asset_types",
    tags=["asset types"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_asset_type_handler(
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get asset types")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_asset_type_handler(
    asset_type: AssetTypeCreate,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(asset_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create asset type")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_asset_type_handler(
    uuid: str,
    updated_asset_type: AssetType,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_asset_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update asset type")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_asset_type_handler(
    uuid: str,
    service: AssetTypeService = Depends(Provide[Container.asset_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Asset Type deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete asset type")
