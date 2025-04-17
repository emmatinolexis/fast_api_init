from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from app.client.redis import RedisClient
from fastapi.encoders import jsonable_encoder

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.service.activity_log_service import ActivityLogService
from app.util.utils import (
    pagination,
    send_client_side_error,
    send_data_with_info,
    send_data_with_pagination,
    send_internal_server_error,
    total_pages,
    send_data,
)

router = APIRouter(
    prefix="/activity_logs",
    tags=["activity_logs"],
)

msg_prefix = "Activity Log"


admin_router = APIRouter(
    prefix="/admin/activity_logs",
    tags=["admin_activity_logs"],
)

redis = RedisClient()


@router.get("/business", response_class=ORJSONResponse)
@inject
async def get_business_activity_logs(
    start_date: str = None,
    end_date: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    activity_types: List[str] = Query(None, description="List of activity types"),
    search_string: str = None,
    service: ActivityLogService = Depends(Provide[Container.activity_log_service]),
    current_user: User = Depends(
        get_current_user_with_permission("view_business_activity_log")
    ),
):
    try:

        logs_count = await service.count_business_activity_logs(
            current_user.business_profile_uuid,
            start_date,
            end_date,
            activity_types,
            search_string,
        )

        pagination_data = pagination(
            total=logs_count,
            limit=page_size,
            current_page=page,
            total_pages=total_pages(logs_count, page_size),
        )

        # Create unique cache key
        cache_key = (
            f"business_activity_logs:{current_user.business_profile_uuid}:{start_date}:{end_date}:"
            f"{activity_types}:{search_string}:{page}:{page_size}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        logs = await service.business_activity_logs(
            current_user.business_profile_uuid,
            start_date,
            end_date,
            page,
            page_size,
            activity_types,
            search_string,
        )

        response_payload = {
            "data": jsonable_encoder(logs),
            "pagination": jsonable_encoder(pagination_data),
        }

        await redis.set_cache(cache_key, response_payload)

        return send_data_with_pagination(pagination=pagination_data, data=logs)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@admin_router.get("/", response_class=ORJSONResponse)
@inject
async def get_admin_activity_logs(
    start_date: str = None,
    end_date: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    activity_types: List[str] = Query(None, description="List of activity types"),
    service: ActivityLogService = Depends(Provide[Container.activity_log_service]),
    search_string: str = None,
    current_user: User = Depends(
        get_current_user_with_permission("view_admin_activity_log")
    ),
):
    try:

        logs_count = await service.count_admin_activity_logs(
            start_date, end_date, activity_types, search_string
        )

        pagination_data = pagination(
            total=logs_count,
            limit=page_size,
            current_page=page,
            total_pages=total_pages(logs_count, page_size),
        )

        # Create unique cache key
        cache_key = (
            f"admin_activity_logs:{current_user.business_profile_uuid}:{start_date}:{end_date}:"
            f"{activity_types}:{search_string}:{page}:{page_size}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        logs = await service.admin_activity_logs(
            start_date, end_date, page, page_size, activity_types, search_string
        )

        data = {"data": logs, "pagination": pagination_data}

        await redis.set_cache(cache_key, data)

        return send_data_with_pagination(pagination=pagination_data, data=logs)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@admin_router.get("/general", response_class=ORJSONResponse)
@inject
async def get_all_logs_handler(
    start_date: str = None,
    end_date: str = None,
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    activity_types: List[str] = Query(None, description="List of activity types"),
    service: ActivityLogService = Depends(Provide[Container.activity_log_service]),
    search_string: str = None,
    current_user: User = Depends(
        get_current_user_with_permission("view_all_activity_log")
    ),
):
    try:

        logs_count = await service.count_activity_logs(
            start_date, end_date, activity_types, search_string
        )

        pagination_data = pagination(
            total=logs_count,
            limit=page_size,
            current_page=page,
            total_pages=total_pages(logs_count, page_size),
        )

        # Create unique cache key
        cache_key = (
            f"general_activity_logs:{current_user.business_profile_uuid}:{start_date}:{end_date}:"
            f"{activity_types}:{search_string}:{page}:{page_size}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        logs = await service.all_activity_logs(
            start_date, end_date, page, page_size, activity_types, search_string
        )

        data = {"data": logs, "pagination": pagination_data}

        await redis.set_cache(cache_key, data)

        return send_data_with_pagination(pagination=pagination_data, data=logs)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{log_uuid}", response_class=ORJSONResponse)
@inject
async def get_activity_log_details(
    log_uuid: str,
    service: ActivityLogService = Depends(Provide[Container.activity_log_service]),
    current_user: User = Depends(get_current_user_with_permission("view_activity_log")),
):
    try:
        log = await service.get_activity_log(log_uuid=log_uuid)
        return send_data_with_info(data=log, info=messages.GET_SUCCESS + msg_prefix)
    except NotFoundError as e:
        return send_client_side_error(e.detail)
    except Exception as e:
        return send_internal_server_error(
            user_msg=messages.GET_FAILED + msg_prefix, error=str(e)
        )
