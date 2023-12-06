import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.equipment_schema import EquipmentType, EquipmentTypeCreate
from app.service.equipment_type_service import EquipmentTypeService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/equipment_types",
    tags=["equipment types"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_equipment_types_handler(
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get equipment types")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_equipment_type_handler(
    equipment_type: EquipmentTypeCreate,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(equipment_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create equipment type")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_equipment_type_handler(
    uuid: str,
    updated_equipment_type: EquipmentType,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_equipment_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update equipment type")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_equipment_type_handler(
    uuid: str,
    service: EquipmentTypeService = Depends(Provide[Container.equipment_type_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Equipment type deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete equipment type")
