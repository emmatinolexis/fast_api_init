from datetime import date
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestError, NotFoundError
from app.model.user import User
from app.schema.asset_schema import DriverPayload
from app.service.asset_operator_assignment_service import AssetOperatorAssignmentService
from app.service.driver_license_service import DriverLicenseService
from app.service.driver_service import DriverService
from app.service.user_service import UserService
from app.util.email import send_license_expiry_email
from app.util.enums import ActiveStatus
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"],
)
msg_prefix = "driver"


@router.get("/license_expiry")
@inject
async def check_drivers_license_expiry(
    user_service: UserService = Depends(Provide[Container.user_service]),
    service: DriverLicenseService = Depends(Provide[Container.driver_license_service]),
):
    try:
        licenses = service.get_all_licenses()

        for license in licenses:
            if license.expires_soon():
                driver = user_service.get_by_uuid(license.user_id)
                no_days = (license.expiration_date - date.today()).days
                await send_license_expiry_email(
                    recipient_name=f"{driver.first_name} {driver.last_name}",
                    email=driver.email_address,
                    expiry_date=license.expiration_date.strftime("%d %B, %Y"),
                    no_days=no_days,
                )
    except Exception as e:
        msg = messages.LICENSE_CHECK_FAILED
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_drivers_handler(
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_driver_handler(
    payload: DriverPayload,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        existing_driver = service.get_driver_by_phone_number(payload.phone_number)
        if existing_driver:
            msg = f"Driver already exists with phone number {payload.phone_number}"
            return send_internal_server_error(user_msg=msg, error=msg)
        driver = service.create_driver(payload)
        return send_data(driver)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_driver_handler(
    uuid: str,
    payload: DriverPayload,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        driver = service.update_driver(uuid, payload)
        if driver is None:
            return send_client_side_error(user_msg=messages.DRIVER_NOT_FOUND + uuid)
        return send_data(driver)
    except NotFoundError as e:
        return send_client_side_error(user_msg=messages.ASSET_NOT_FOUND + str(e.detail))
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/unassign/{driver_uuid}", response_class=ORJSONResponse)
@inject
async def unassign_driver_handler(
    driver_uuid: str,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.unassign_driver(driver_uuid)
        return send_info(messages.DRIVER_UNASSIGNED_SUCCESS)
    except BadRequestError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_driver_by_uuid_handler(
    uuid: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        driver = user_service.get_driver_by_uuid(uuid)
        return send_data(driver)
    except NotFoundError as e:
        return send_client_side_error(e.detail)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/drivers_by_user/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_drivers_by_user_uuid_handler(
    user_uuid: str,
    service: DriverService = Depends(Provide[Container.driver_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        driver = service.get_drivers_by_user_uuid(user_uuid, page, page_size)
        if driver is None:
            return send_client_side_error(
                user_msg=messages.DRIVER_NOT_FOUND + user_uuid
            )
        return send_data(driver)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/drivers_by_business/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_drivers_by_business_uuid_handler(
    business_uuid: str,
    role_uuid: str,
    status: ActiveStatus = Query(None, description="Status of the operator"),
    operator_type: List[str] = Query(
        None, description="List of operator types: 'rider', 'driver'"
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter drivers by name"
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        drivers = user_service.get_drivers_by_business_uuid(
            business_uuid, role_uuid, page, page_size, operator_type, status, search
        )
        if drivers is None:
            return send_client_side_error(
                user_msg=messages.DRIVER_NOT_FOUND + business_uuid
            )
        return send_data(drivers)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_driver_by_uuid_handler(
    uuid: str,
    service: DriverService = Depends(Provide[Container.driver_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_info(messages.DELETE_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=messages.DRIVER_NOT_FOUND + str(e.detail)
        )
    except Exception as e:
        msg = messages.DELETE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/change")
@inject
async def change_rider_asset_handler(
    asset_uuid: str,
    operator_uuid: str,
    service: AssetOperatorAssignmentService = Depends(
        Provide[Container.asset_operator_assignment_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        response = service.assign_operator_to_asset(
            asset_uuid,
            operator_uuid,
            current_user.uuid,
            current_user.business_profile_uuid,
        )
        return send_info(response)
    except (NotFoundError, BadRequestError) as e:
        return send_client_side_error(user_msg=str(e.detail), dev_msg=str(e.detail))
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
