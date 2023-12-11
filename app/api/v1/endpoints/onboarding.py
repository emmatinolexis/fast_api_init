import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError, NotFoundError
from app.model.user import User
from app.schema.onboarding_schema import BusinessOnboardingPayload, OnboardingPayload
from app.service.onboarding_service import OnboardingService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
)
log = structlog.get_logger()
msg_prefix = "onboarding"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_onboardings_handler(
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_individual_onboarding_handler(
    payload: OnboardingPayload,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        log.debug("testing")
        onboarding = service.create_individual_onboarding(payload)
        return send_data(onboarding)
    except NotFoundError as e:
        return send_client_side_error(user_msg=str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/organisation", response_class=ORJSONResponse)
@inject
async def create_organisation_onboarding_handler(
    payload: BusinessOnboardingPayload,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        onboarding = service.create_business_onboarding(payload)
        return send_data(onboarding)
    except NotFoundError as e:
        return send_client_side_error(user_msg=str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_onboarding_handler(
    uuid: str,
    payload: OnboardingPayload,
    service: OnboardingService = Depends(Provide[Container.onboarding_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, payload))
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
        return send_info("Onboarding deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete onboarding")
