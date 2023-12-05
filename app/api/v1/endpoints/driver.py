import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.asset_schema import Driver
from app.service.driver_service import DriverService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_drivers_handler(
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get drivers")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_driver_handler(
    driver: Driver,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(driver))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create driver")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_driver_handler(
    uuid: str,
    driver: Driver,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, driver))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update driver")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_driver_by_uuid_handler(
    uuid: str,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get driver")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_driver_by_uuid_handler(
    uuid: str,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Driver deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete driver")
