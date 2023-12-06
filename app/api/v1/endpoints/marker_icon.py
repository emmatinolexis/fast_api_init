from typing import List

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.marker_schema import MarkerIcon, MarkerIconFetch
from app.service.marker_icon_service import MarkerIconService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/marker_icons",
    tags=["marker icons"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
async def get_all_marker_icons_handler(
    service: MarkerIconService = Depends(Provide[Container.marker_icon_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get marker icons")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_marker_icon_handler(
    marker_icon: MarkerIcon,
    service: MarkerIconService = Depends(Provide[Container.marker_icon_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(marker_icon))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create marker icon")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_marker_icon_handler(
    uuid: str,
    updated_marker_icon: MarkerIcon,
    service: MarkerIconService = Depends(Provide[Container.marker_icon_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_marker_icon))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update marker icon")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_marker_icon_handler(
    uuid: str,
    service: MarkerIconService = Depends(Provide[Container.marker_icon_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Marker icon deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete marker icon")
