import logging
from typing import List, Optional
from app.client.redis import RedisClient

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.alert_policy_schema import (
    AlertPolicyPayload,
    AlertPolicyUpdatePayload,
    GeofenceAlertPolicyPayload,
    GeofenceAlertPolicyUpdatePayload,
)
from app.service.alert_policy_service import AlertPolicyService
from app.util.email import (
    send_alert_policy_violation_email,
    send_maintenance_alert_email,
)
from app.util.enums import ActiveStatus
from app.util.utils import (
    allow_admins_only,
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/alert_policies",
    tags=["alert policies"],
)
msg_prefix = "alert policy"

redis = RedisClient()


@router.get("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_alert_policies_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user_with_permission("view_policy")),
):
    try:
        return send_data(await service.get_all_alert_policies(page, page_size))
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_policies_by_user_handler(
    user_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    policy_status: Optional[ActiveStatus] = Query(
        None, description="Filter by policy status. Possible values: active, inactive"
    ),
    policy_types: List[str] = Query(
        None,
        description="UUIDs of the policy types to filter by",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD'",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD' ",
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter by relevant fields"
    ),
    current_user: User = Depends(get_current_user_with_permission("view_policy")),
):
    try:
        # Create unique cache key
        cache_key = (
            f"user_alert_policies:{user_uuid}:{policy_status}:{page}:{page_size}:{search}:"
            f"{policy_types}:{start_date}:{end_date}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        data = await service.get_all_alert_policies_by_user(
            user_uuid,
            page,
            page_size,
            policy_status,
            policy_types,
            start_date,
            end_date,
            search,
        )
        # Cache the result for 24 hours
        await redis.set_cache(cache_key, data)
        return send_data(data)
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/business/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_policies_by_business_handler(
    business_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    policy_status: Optional[ActiveStatus] = Query(
        None, description="Filter by policy status. Possible values: active, inactive"
    ),
    policy_types: List[str] = Query(
        None,
        description="UUIDs of the policy types to filter by",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD'",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD' ",
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter by relevant fields"
    ),
    current_user: User = Depends(get_current_user_with_permission("view_policy")),
):
    try:
        # Create unique cache key
        cache_key = (
            f"business_alert_policies:{business_uuid}:{policy_status}:{page}:{page_size}:{search}:"
            f"{policy_types}:{start_date}:{end_date}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        data = await service.get_all_alert_policies_by_business(
            business_uuid,
            page,
            page_size,
            policy_status,
            policy_types,
            start_date,
            end_date,
            search,
        )

        # Cache the result for 24 hours
        await redis.set_cache(cache_key, data)

        return send_data(data)
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/alert_violations/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_violations_by_user_handler(
    user_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    policy_type: Optional[str] = Query(
        None,
        description="Filter by policy type. Possible values: Geofence alert policy, Over speeding alert policy",
    ),
    policy_status: Optional[str] = Query(
        None, description="Filter by policy status. Possible values: active, inactive"
    ),
    start_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD'",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD' ",
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter by relevant fields"
    ),
    current_user: User = Depends(
        get_current_user_with_permission("view_alert_violations")
    ),
):
    try:
        # Create unique cache key
        cache_key = (
            f"user_alert_violations:{user_uuid}:{policy_status}:{page}:{page_size}:{search}:"
            f"{policy_type}:{start_date}:{end_date}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        alerts = await service.get_all_alert_violations_by_user(
            user_uuid=user_uuid,
            page=page,
            page_size=page_size,
            policy_type=policy_type,
            policy_status=policy_status,
            start_date=start_date,
            end_date=end_date,
            search=search,
        )

        await redis.set_cache(cache_key, alerts, 60 * 5)

        return send_data(alerts)
    except Exception as e:
        msg = messages.GET_FAILED + "alert violations"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/alert_violations/business/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_violations_by_business_handler(
    business_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    policy_status: ActiveStatus = Query(
        None, description="Filter by policy status. Possible values: active, inactive"
    ),
    policy_types: List[str] = Query(
        None,
        description="Filter by policy type. Possible values: Geofence alert policy, Over speeding alert policy",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD'",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter by date or date range in format 'YYYY-MM-DD' ",
    ),
    search: Optional[str] = Query(
        None, description="Search term to filter by relevant fields"
    ),
    current_user: User = Depends(
        get_current_user_with_permission("view_alert_violations")
    ),
):
    try:
        # Create unique cache key
        cache_key = (
            f"business_alert_violations:{business_uuid}:{policy_status}:{page}:{page_size}:{search}:"
            f"{policy_types}:{start_date}:{end_date}"
        )

        # Check if result is cached
        cached = await redis.get_cache(cache_key)
        if cached:
            return send_data(cached)

        data = await service.get_all_alert_violations_by_business(
            business_uuid,
            page,
            page_size,
            policy_status,
            policy_types,
            start_date,
            end_date,
            search,
        )

        await redis.set_cache(cache_key, data, 60 * 5)

        return send_data(data)
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_policy_handler(
    payload: AlertPolicyPayload,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("create_policy")),
):
    try:
        alert_policy = await service.create_alert_policy(
            payload, current_user.uuid, current_user.business_profile_uuid
        )
        await redis.delete_by_pattern(
            f"business_alert_policies:{current_user.business_profile.uuid}*"
        )
        await redis.delete_by_pattern(f"user_alert_policies:{current_user.uuid}*")

        logging.info(f"Created alert policy: {alert_policy}")
        return send_data(alert_policy)
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/geofence", response_class=ORJSONResponse)
@inject
async def create_geofence_alert_policy_handler(
    payload: GeofenceAlertPolicyPayload,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("create_policy")),
):
    try:
        alert_policy = await service.create_geofence_alert_policy(
            payload, str(current_user.uuid), str(current_user.business_profile_uuid)
        )

        await redis.delete_by_pattern(
            f"business_alert_policies:{current_user.business_profile.uuid}*"
        )
        await redis.delete_by_pattern(f"user_alert_policies:{current_user.uuid}*")

        logging.info(f"Created alert policy: {alert_policy}")
        return send_data(alert_policy)
    except NotFoundError as e:
        return send_client_side_error(user_msg=str(e))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.patch("/geofence/{geofence_uuid}", response_class=ORJSONResponse)
@inject
async def update_geofence_alert_policy_handler(
    payload: GeofenceAlertPolicyUpdatePayload,
    geofence_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("update_policy")),
):
    try:
        alert_policy = await service.update_geofence_alert_policy(
            payload, geofence_uuid
        )

        await redis.delete_by_pattern(
            f"business_alert_policies:{current_user.business_profile.uuid}*"
        )
        await redis.delete_by_pattern(f"user_alert_policies:{current_user.uuid}*")

        return send_data(alert_policy)
    except NotFoundError as e:
        return send_client_side_error(user_msg=str(e))
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/geofence/check", response_class=ORJSONResponse)
@inject
async def check_geofence_violation_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
):
    try:
        response_data = await service.check_geofence_violation()

        violations = response_data.get("violations", [])

        if violations:
            for violation in violations:
                for alert_recipient in violation.get("alert_recipients", []):
                    if "@" in alert_recipient.get("recipient"):
                        recipient_name = "MVI User"
                        email = alert_recipient.get("recipient")
                        asset_name = violation.get("asset").get("asset_name")
                        policy_name = violation.get("alert_policy").get("policy_name")

                        # Send email for each violation
                        await send_alert_policy_violation_email(
                            recipient_name,
                            email,
                            asset_name,
                            policy_name,
                        )
                        logging.info(f"Policy violation for {policy_name}")
                        pass
                    else:
                        # send sms notification
                        # await send_sms('0541557459', 'Violation sms test')

                        pass

        return response_data

    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/over_speeding/check", response_class=ORJSONResponse)
@inject
async def check_over_speeding_violation_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
):
    try:
        response_data = await service.check_over_speeding_violation()

        violations = response_data.get("violations", [])

        if violations:
            for violation in violations:
                for alert_recipient in violation.get("alert_recipients", []):
                    if "@" in alert_recipient.get("recipient"):
                        recipient_name = "MVI User"
                        email = alert_recipient.get("recipient")
                        asset_name = violation.get("asset").get("asset_name")
                        policy_name = violation.get("alert_policy").get("policy_name")

                        # Send email for each violation
                        await send_alert_policy_violation_email(
                            recipient_name,
                            email,
                            asset_name,
                            policy_name,
                        )
                        logging.info(f"Policy violation for {policy_name}")
                    else:
                        # send sms notification
                        pass

        return response_data

    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/idling/check", response_class=ORJSONResponse)
@inject
async def check_idling_violation_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
):
    try:
        response_data = await service.check_idling_violation()

        violations = response_data.get("violations", [])

        if violations:
            for violation in violations:
                for alert_recipient in violation.get("alert_recipients", []):
                    if "@" in alert_recipient.get("recipient"):
                        recipient_name = "MVI User"
                        email = alert_recipient.get("recipient")
                        asset_name = violation.get("asset").get("asset_name")
                        policy_name = violation.get("alert_policy").get("policy_name")

                        # Send email for each violation
                        await send_alert_policy_violation_email(
                            recipient_name,
                            email,
                            asset_name,
                            policy_name,
                        )
                        logging.info(f"Policy violation for {policy_name}")
                    else:
                        # send sms notification
                        pass

        return response_data

    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/maintenance/check", response_class=ORJSONResponse)
@inject
async def check_maintenance_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
):
    try:
        response_data = await service.check_maintenance()

        violations = response_data.get("violations", [])

        if violations:
            for violation in violations:
                for alert_recipient in violation.get("alert_recipients", []):
                    if "@" in alert_recipient.get("recipient"):
                        recipient_name = "MVI User"
                        email = alert_recipient.get("recipient")
                        asset_name = violation.get("asset").get("asset_name")
                        policy_name = violation.get("alert_policy").get("policy_name")

                        # Send email for each violation
                        await send_maintenance_alert_email(
                            recipient_name, email, asset_name, policy_name
                        )
                        logging.info(f"Policy violation for {policy_name}")
                    else:
                        # send sms notification
                        pass

        return response_data

    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.put("/{alert_uuid}", response_class=ORJSONResponse)
@inject
async def toggle_alert_status_handler(
    alert_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("update_policy")),
):
    try:
        return send_data(await service.toggle_alert_status(alert_uuid))
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put(
    "/alert_violations/status/{alert_violation_uuid}", response_class=ORJSONResponse
)
@inject
async def toggle_alert_violations_status_handler(
    alert_violation_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(
        get_current_user_with_permission("update_alert_violations")
    ),
):
    try:
        return send_data(
            await service.toggle_alert_violation_status(alert_violation_uuid)
        )
    except Exception as e:
        msg = messages.GET_FAILED + "alert policies"
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{alert_uuid}", response_class=ORJSONResponse)
@inject
async def update_alert_policy_handler(
    alert_uuid: str,
    payload: AlertPolicyUpdatePayload,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("update_policy")),
):
    try:
        data = await service.update_alert_policy(alert_uuid, payload)
        return send_data_with_info(
            data=data, info=messages.UPDATE_SUCCESS + "alert policy"
        )
    except NotFoundError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{maintenance_alert_uuid}/toggle_status", response_class=ORJSONResponse)
@inject
async def toggle_maintenance_alert(
    maintenance_alert_uuid: str,
    date: str = None,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("update_policy")),
):
    try:
        updated_alert = await service.toggle_maintenance_status(
            maintenance_alert_uuid, date
        )
        return updated_alert
    except Exception as e:
        msg = messages.MAINTENANCE_UPDATED_FAILED
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/get_alert_reminders/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_reminders(
    user_uuid: str,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user_with_permission("view_policy")),
):
    try:
        reminders = await service.get_all_alert_reminders(user_uuid)
        return send_data(reminders)
    except Exception as e:
        msg = messages.ALERT_REMINDERS_NOT_FOUND + user_uuid
        return send_internal_server_error(user_msg=msg, error=e)
