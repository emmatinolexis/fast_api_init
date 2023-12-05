import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.package_schema import PackageItem
from app.service.package_item_service import PackageItemService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/package_items",
    tags=["package items"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_package_items_handler(
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get package items")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_package_item_handler(
    package_item: PackageItem,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(package_item))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create package item")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_package_item_handler(
    uuid: str,
    updated_package_item: PackageItem,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_package_item))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update package item")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_package_item_handler(
    uuid: str,
    service: PackageItemService = Depends(Provide[Container.package_item_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Package Item deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete package item")
