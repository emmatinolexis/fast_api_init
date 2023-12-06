import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.package_schema import Package, PackageItemAssignment
from app.service.package_service import PackageService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/packages",
    tags=["packages"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_packages_handler(
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_packages())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get packages")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_package_handler(
    package: Package,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(package))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create package")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_package_handler(
    uuid: str,
    updated_package: Package,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_package))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update package")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_package_by_uuid_handler(
    uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.read_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get package")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_package_by_uuid_handler(
    uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Package deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete package")


@router.post("/package_assignment", response_model=None)
@inject
async def assign_package_handler(
    data: PackageItemAssignment,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.assign_package_item(data))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update package item")


@router.delete(
    "/package_assignment/{package_uuid}/{package_item_uuid}",
    response_class=ORJSONResponse,
)
@inject
async def delete_package_from_package_handler(
    package_uuid: str,
    package_item_uuid: str,
    service: PackageService = Depends(Provide[Container.package_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.delete_package_item(package_uuid, package_item_uuid)
        return send_message("Package item deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete package item")
