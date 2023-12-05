from typing import List

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.onboarding_schema import OrganisationContact
from app.service.organisation_contact_service import OrganisationContactService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/organisation_contacts",
    tags=["organisation contacts"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_contacts_handler(
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get organisation_contacts")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_contact_handler(
    organisation_contact: OrganisationContact,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(organisation_contact))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create organisation_contact")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_contact_handler(
    uuid: str,
    organisation_contact: OrganisationContact,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, organisation_contact))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update organisation_contact")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_contact_by_uuid_handler(
    uuid: str,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get organisation_contact")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_contact_by_uuid_handler(
    uuid: str,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Organisation Contact deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete organisation_contact")
