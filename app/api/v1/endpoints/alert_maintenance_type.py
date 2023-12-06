import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.asset_schema import AlertMaintenanceType
from app.service.alert_maintenance_type_service import AlertMaintenanceTypeService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/alert_maintenance_types",
    tags=["alert maintenance types"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_alert_maintenance_types_handler(
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get alert maintenance types")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_maintenance_type_handler(
    alert_maintenance_type: AlertMaintenanceType,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(alert_maintenance_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create alert maintenance type")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_alert_maintenance_type_handler(
    uuid: str,
    updated_alert_maintenance_type: AlertMaintenanceType,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_alert_maintenance_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update alert maintenance type")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_alert_maintenance_type_by_uuid_handler(
    uuid: str,
    service: AlertMaintenanceTypeService = Depends(
        Provide[Container.alert_maintenance_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Alert maintenance type deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete alert maintenance type")
