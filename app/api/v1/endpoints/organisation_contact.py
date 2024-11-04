from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.onboarding_schema import OrganisationContactPayload
from app.service.organisation_contact_service import OrganisationContactService
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/organisation_contacts",
    tags=["organisation contacts"],
)
msg_prefix = "organisation contact"


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
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)




@router.post("/", response_class=ORJSONResponse)
@inject
async def create_contact_handler(
    payload: OrganisationContactPayload,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        contact = service.create_organisation_contact(payload)
        return send_data(contact)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.USER_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_contact_handler(
    uuid: str,
    payload: OrganisationContactPayload,
    service: OrganisationContactService = Depends(
        Provide[Container.organisation_contact_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        contact = service.update_organisation_contact(uuid, payload)
        if contact is None:
            return send_client_side_error(
                user_msg=messages.ORGANISATION_CONTACT_NOT_FOUND + uuid
            )
        return send_data(contact)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.USER_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


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
        contact = service.get_by_uuid(uuid)
        if contact is None:
            return send_client_side_error(
                user_msg=messages.ORGANISATION_CONTACT_NOT_FOUND + uuid
            )
        return send_data(contact)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


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
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.ORGANISATION_CONTACT_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
