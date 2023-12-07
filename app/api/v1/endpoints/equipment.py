# from typing import List

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.equipment_schema import Equipment
from app.service.equipment_service import EquipmentService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/equipments",
    tags=["equipments"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_equipments_handler(
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get equipments")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_equipment_handler(
    equipment: Equipment,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(equipment))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create equipment")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_equipment_handler(
    uuid: str,
    updated_equipment: Equipment,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_equipment))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update equipment")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_equipment_handler(
    uuid: str,
    service: EquipmentService = Depends(Provide[Container.equipment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Equipment deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete equipment")
