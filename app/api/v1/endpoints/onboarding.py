from typing import List

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.onboarding_schema import Onboarding
from app.service.driver_service import OnboardingService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_onboardings_handler(
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get onboarding")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_individual_onboarding_handler(
    onboarding: Onboarding,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.create_individual_onboarding(onboarding))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create onboarding")


@router.post("/organisation", response_class=ORJSONResponse)
@inject
async def create_organisation_onboarding_handler(
    onboarding: Onboarding,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.create_business_onboarding(onboarding))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create onboarding")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_onboarding_handler(
    uuid: str,
    onboarding: Onboarding,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, onboarding))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update onboarding")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_onboarding_by_uuid_handler(
    uuid: str,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get onboarding")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_onboarding_by_uuid_handler(
    uuid: str,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Onboarding deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete onboarding")
