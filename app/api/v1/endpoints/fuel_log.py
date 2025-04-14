from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from app.client.redis import RedisClient

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.fuel_log_schema import FuelLogSchema, SingleFuelLog, UpdateFuelLog
from app.service.fuel_log_service import FuelLogService
from app.service.user_service import UserService
from app.core.constants import OPERATOR_ROLE_NAME
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/fuel_logs",
    tags=["fuel_logs"],
)
msg_prefix = "fuel_log"

redis = RedisClient()


@router.post("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_fuel_log_handler_for_individual(
    user_uuid: str,
    payload: FuelLogSchema,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(
        get_current_user_with_permission("create_fuel_purchase_log")
    ),
):
    try:
        user = await user_service.get_user_by_uuid(user_uuid)

        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND, status_code=404
            )

        business_profile_uuid = str(user.get("business_profile").uuid)

        data = await service.create_individual_fuel_log(
            payload, user_uuid, business_profile_uuid
        )
        await redis.delete_by_pattern(
            f"fuel_logs:{current_user.business_profile.uuid}*"
        )

        return send_data(data)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=404, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.post("/fleet_manager_bulk/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_bulk_fuel_logs_handler(
    user_uuid: str,
    csv_url: str,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(
        get_current_user_with_permission("create_fuel_purchase_log")
    ),
):
    try:
        user = await user_service.get_user_by_uuid(user_uuid)
        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND, status_code=404
            )

        await service.create_bulk_fuel_logs(
            user_uuid,
            csv_url,
            (
                str(user.get("business_profile").uuid)
                if user.get("business_profile").uuid
                else None
            ),
        )

        await redis.delete_by_pattern(
            f"fuel_logs:{current_user.business_profile.uuid}*"
        )

        return send_info(messages.CSV_LOAD_SUCCESS)
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.CSV_LOAD_FAILED
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/fleet_manager_single/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_fuel_log_handler_for_fleet_manager(
    user_uuid: str,
    payload: SingleFuelLog,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(
        get_current_user_with_permission("create_fuel_purchase_log")
    ),
):
    try:
        user = await user_service.get_user_by_uuid(user_uuid)

        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND, status_code=404
            )

        data = await service.create_fleet_manager_single_fuel_log(
            payload,
            user_uuid,
            (
                str(user.get("business_profile").uuid)
                if user.get("business_profile").uuid
                else None
            ),
        )

        await redis.delete_by_pattern(
            f"fuel_logs:{current_user.business_profile.uuid}*"
        )

        return send_data_with_info(data, messages.CREATE_SUCCESS + "fuel log")
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_fuel_logs_handler(
    user_uuid: str,
    page: int = Query(1, gt=0, description="Page number"),
    page_size: int = Query(10, gt=0, description="Page size"),
    search: str = Query(None, description="Search query"),
    start_date: str = Query(None, description="Start date"),
    end_date: str = Query(None, description="End date"),
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(
        get_current_user_with_permission("view_fuel_purchase_log")
    ),
):
    try:

        user = await user_service.get_user_by_uuid(user_uuid)
        business_profile_uuid = str(user.get("business_profile").uuid)

        # Create unique cache key
        cache_key = (
            f"fuel_logs:{business_profile_uuid}:{user_uuid}:{search}:{page}:{page_size}:"
            f"{start_date}:{end_date}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        if business_profile_uuid != str(current_user.business_profile.uuid):
            return send_client_side_error(
                messages.NOT_AUTHORIZED,
                messages.NOT_AUTHORIZED,
                403,
            )

        if not user:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND, status_code=404
            )

        data = await service.get_fuel_logs_by_business_uuid(
            business_uuid=business_profile_uuid,
            user_uuid=(
                str(current_user.uuid)
                if current_user.user_role.role_name == OPERATOR_ROLE_NAME
                else None
            ),
            page=page,
            page_size=page_size,
            search=search,
            start_date=start_date,
            end_date=end_date,
        )

        await redis.set_cache(cache_key, data)

        return send_data_with_info(data, messages.GET_SUCCESS + "fuel logs")
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/receipt/{fuel_log_uuid}", response_class=ORJSONResponse)
@inject
async def upload_fuel_log_receipt_handler(
    fuel_log_uuid: str,
    payload: UpdateFuelLog,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    current_user: User = Depends(
        get_current_user_with_permission("create_fuel_purchase_log")
    ),
):
    try:
        log_entry = await service.get_by_uuid(fuel_log_uuid)
        if not log_entry:
            user_msg = messages.FUEL_LOG_NOT_FOUND + fuel_log_uuid
            return send_client_side_error(
                user_msg=user_msg, dev_msg=user_msg, status_code=404
            )

        if log_entry.business_profile_uuid != current_user.business_profile_uuid:
            return send_client_side_error(
                user_msg=messages.ACTION_NOT_ALLOWED,
                dev_msg=messages.ACTION_NOT_ALLOWED,
                status_code=401,
            )

        data = await service.update_fuel_log_receipt(fuel_log_uuid, payload)
        await redis.delete_by_pattern(
            f"fuel_logs:{current_user.business_profile.uuid}*"
        )

        return send_data_with_info(data, messages.UPDATE_SUCCESS + "fuel log")
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/receipt/{fuel_log_uuid}", response_class=ORJSONResponse)
@inject
async def get_fuel_log_receipt_handler(
    fuel_log_uuid: str,
    service: FuelLogService = Depends(Provide[Container.fuel_log_service]),
    current_user: User = Depends(
        get_current_user_with_permission("view_fuel_purchase_log")
    ),
):
    try:
        log_entry = await service.get_by_uuid(fuel_log_uuid)
        if not log_entry:
            user_msg = messages.FUEL_LOG_NOT_FOUND + fuel_log_uuid
            return send_client_side_error(
                user_msg=user_msg, dev_msg=user_msg, status_code=404
            )

        if log_entry.business_profile_uuid != current_user.business_profile_uuid:
            return send_client_side_error(
                user_msg=messages.ACTION_NOT_ALLOWED,
                dev_msg=messages.ACTION_NOT_ALLOWED,
                status_code=401,
            )

        data = await service.get_receipt_by_uuid(fuel_log_uuid)

        return send_data_with_info(data, messages.GET_SUCCESS + "fuel log")
    except NotFoundError as e:
        return send_client_side_error(
            user_msg=e.detail, status_code=401, dev_msg=e.detail
        )
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
