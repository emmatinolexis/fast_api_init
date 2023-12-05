from typing import List

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.feature_schema import Feature
from app.service.feature_service import FeatureService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/features",
    tags=["features"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_features_handler(
    service: FeatureService = Depends(Provide[Container.feature_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get features")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_feature_handler(
    feature: Feature,
    service: FeatureService = Depends(Provide[Container.feature_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(feature))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create feature")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_feature_handler(
    uuid: str,
    feature: Feature,
    service: FeatureService = Depends(Provide[Container.feature_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, feature))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update feature")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_feature_by_uuid_handler(
    uuid: str,
    service: FeatureService = Depends(Provide[Container.feature_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get feature")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_feature_by_uuid_handler(
    uuid: str,
    service: FeatureService = Depends(Provide[Container.feature_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Feature deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete feature")
