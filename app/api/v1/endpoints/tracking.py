import json
import logging
import socket
import ssl
from datetime import datetime, timedelta
from typing import Optional
from app.client.redis import RedisClient


from cryptography import x509
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.model.user import User
from app.schema.tracking_device_schema import (
    DeviceReportPayload,
    DeviceReportPayloadInput,
)
from app.service.asset_service import AssetService
from app.service.device_alert_notification_service import DeviceAlertNotificationService
from app.service.device_events_service import DeviceEventService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.service.tracking_event_service import TrackingEventService
from app.service.tracking_event_backup_service import TrackingEventBackupService
from app.service.user_service import UserService
from app.util.email import EmailPurpose, send_device_alert_email
from app.util.enums import FileFormat
from app.util.sms import send_sms
from app.schema.tracking_event_backup_schema import TrackingEventBackupSchema
from app.util.utils import (
    get_content_type,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
    upload_to_s3,
)

router = APIRouter(
    prefix="/tracking",
    tags=["device_events"],
)
msg_prefix = "device events"

redis = RedisClient()


@router.get("/inactive_devices", response_class=ORJSONResponse)
@inject
async def check_inactive_devices(
    page: int = Query(1, ge=1, description="Page number, default is 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Number of items per page, default is 10"
    ),
    tracking_service: TrackingEventService = Depends(
        Provide[Container.tracking_event_service]
    ),
):
    try:
        paginated_inactive_assets = await tracking_service.get_inactive_assets(
            page=page, page_size=page_size
        )
        return send_data(paginated_inactive_assets)
    except Exception as e:
        return send_internal_server_error(
            user_msg=messages.INTERNAL_SERVER_ERROR, error=e
        )


@router.get("/check_imei", response_class=ORJSONResponse)
@inject
async def check_imei_exists(
    device_imei: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
):
    try:
        response = await service.get_tracking_device_events(device_imei=device_imei)
        return send_data(response)
    except Exception as e:
        return send_internal_server_error(
            user_msg=messages.INTERNAL_SERVER_ERROR, error=e
        )


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_last_tracking_details_handler(
    device_imei: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
):
    try:
        events = await service.get_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)
        return send_data(events)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/ssl_certificate", response_class=ORJSONResponse)
async def get_ssl_certificate():
    try:
        # Set the hostname
        hostname = "mvitracking-uat.sageinfrastructure.net"

        # Create SSL context
        context = ssl.create_default_context()
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_default_certs()

        # Connect to the server
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get the full certificate chain in DER format
                der_cert_chain = ssock.getpeercert(True)  # Get raw DER certificate

                # Convert DER to PEM
                pem_cert = ssl.DER_cert_to_PEM_cert(der_cert_chain)

                # Parse the certificate
                cert = x509.load_pem_x509_certificate(pem_cert.encode())

                # Extract Issuer and Subject
                issuer = cert.issuer.rfc4514_string()
                subject = cert.subject.rfc4514_string()

                # Check if it is the ISRG Root X1 certificate
                if "ISRG Root X1" in issuer or "ISRG Root X1" in subject:
                    return {"certificate": pem_cert}

                return {"error": "ISRG Root X1 certificate not found"}

    except Exception as e:
        return ORJSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/archive/s3", response_class=ORJSONResponse)
@inject
async def archive_tracking_events_handler(
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    backup_service: TrackingEventBackupService = Depends(
        Provide[Container.tracking_event_backup_service]
    ),
    start_date: Optional[str] = Query(
        None, description="Filter by date in dd/mm/yyyy format, default is 3 months ago"
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter by date in dd/mm/yyyy format, default is the current date",
    ),
):
    try:
        if not start_date or not end_date:
            end_date = (datetime.utcnow() - timedelta(days=30)).strftime(
                "%d/%m/%Y"
            )  # One month ago from today
            start_date = (datetime.utcnow() - timedelta(days=60)).strftime("%d/%m/%Y")

        backup = await backup_service.get_backup_by_date_range(start_date, end_date)

        if backup:
            return send_client_side_error(
                messages.BACKUP_FOUND_MSG, messages.BACKUP_FOUND_MSG
            )

        events = await service.archive_tracking_events(start_date, end_date)

        if events:
            backup_json = json.dumps(events, indent=4, default=str)

            file_format = FileFormat.JSON
            content_type = get_content_type(file_format)
            file_content = backup_json.encode("utf-8")

            url = await upload_to_s3(
                file_name=f"{start_date.replace('/', '-')}_{end_date.replace('/', '-')}.{file_format}",
                file_content=file_content,
                content_type=content_type,
                folder_name="tracking_events",
            )

            # create backup record
            await backup_service.add(
                TrackingEventBackupSchema(
                    start_date=start_date, end_date=end_date, backup_url=url
                )
            )

            # delete archived events
            await service.delete_archived_events(start_date, end_date)

            return send_data(url)
        return send_client_side_error(user_msg=messages.NO_DATA)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}", response_class=ORJSONResponse)
@inject
async def get_tracking_details_by_user_handler(
    user_uuid: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
):
    try:
        # Build cache key using the parameters
        cache_key = f"tracking_details:{user_uuid}:{date}"

        # Check Redis cache first
        cached_data = await redis.get_cache(cache_key)
        if cached_data:
            return send_data(cached_data)

        events = await service.get_events_by_user(date=date, user_uuid=user_uuid)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)

        await redis.set_cache(cache_key, cached_data)

        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/business/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_tracking_details_by_business_handler(
    business_uuid: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    date: str = Query(
        None,
        description="Filter by date in dd/mm/yyyy format, default is the current date",
    ),
):
    try:
        if not date:
            date = datetime.now().strftime("%d/%m/%Y")
        # Build cache key using the parameters
        cache_key = f"tracking_details:{business_uuid}:{date}:{page}:{page_size}"

        # Check Redis cache first
        cached_data = await redis.get_cache(cache_key)
        if cached_data:
            return send_data(cached_data)

        events = await service.get_events_by_user(
            date=date, business_uuid=business_uuid, page=page, page_size=page_size
        )
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)

        await redis.set_cache(cache_key, events)

        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/route_replay/{device_imei}", response_class=ORJSONResponse)
@inject
async def get_route_replay_tracking_details_handler(
    device_imei: str,
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    date: str = None,
):
    try:
        cache_key = f"route_replay:{device_imei}:{date or 'all'}"

        # Check Redis cache
        cached_data = await redis.get_cache(cache_key)
        if cached_data:
            return send_data(cached_data)

        events = await service.get_route_replay_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)

        await redis.set_cache(cache_key, events)

        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/speed_statistics/{asset_uuid}", response_class=ORJSONResponse)
@inject
async def get_over_speeding_stats_handler(
    asset_uuid: str,
    date_from: datetime = Query(
        description="Filter by date in 2025-02-15 00:34:56.789123 format, default is the current date",
    ),
    date_to: datetime = Query(
        description="Filter by date in 2025-02-15 00:34:56.789123 format, default is the current date",
    ),
    tracking_service: TrackingEventService = Depends(
        Provide[Container.tracking_event_service]
    ),
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = await asset_service.get_by_uuid(asset_uuid)

        if asset is None:
            msg = f"{messages.ASSET_NOT_FOUND}{asset_uuid}"
            return send_client_side_error(msg)
        if asset.device_imei is None:
            msg = "Asset not linked to a device"
            return send_client_side_error(msg)
        # Create unique cache key
        cache_key = (
            f"speed_stats:{asset_uuid}:{date_from.isoformat()}:{date_to.isoformat()}"
        )

        # Try fetching from Redis cache
        cached_data = await redis.get_cache(cache_key)
        if cached_data:
            return send_data(cached_data)

        speeding_data = await tracking_service.get_asset_average_speed(
            asset.device_imei, date_from, date_to
        )

        await redis.set_cache(cache_key, speeding_data)

        return send_data(speeding_data)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/device_event", response_class=ORJSONResponse)
@inject
async def create_device_events(
    device_event_payload: DeviceReportPayload,
    service: DeviceEventService = Depends(Provide[Container.device_events_service]),
    device_alert_service: DeviceAlertNotificationService = Depends(
        Provide[Container.device_alert_notification_service]
    ),
    user_service: UserService = Depends(Provide[Container.user_service]),
    peripheral_device_service: PeripheralDeviceService = Depends(
        Provide[Container.peripheral_device_service]
    ),
    current_user: User = Depends(get_current_app_service),
):
    try:
        # Iterate over all measurements in the dataset and extract the fields
        measurements = [
            {
                "quantity": measurement.q,
                "value": measurement.v,
                "type": measurement.t,
                "unit": measurement.u,
            }
            for measurement in device_event_payload.dataset
        ]

        # Creating the data object with the full measurements list
        data = DeviceReportPayloadInput(
            node_id=device_event_payload.node_id,
            gateway_id=device_event_payload.gtwy_id,
            alert_type=device_event_payload.alert_type,
            device_type=device_event_payload.dev_type,
            requires_attention=device_event_payload.has_alert,
            alert_description=device_event_payload.alert_desc,
            measurements=measurements,
            event_datetime=device_event_payload.timestamp,
        )
        # return data
        # Calling the service to add the data
        await service.add(data)

        # check if payload.has_alert is true and send email and sms
        if device_event_payload.has_alert:
            peripheral_device = await peripheral_device_service.get_device_by_node_id(
                device_event_payload.node_id
            )

            if not peripheral_device:
                send_client_side_error(messages.PERIPHERAL_DEVICE_NOT_FOUND_MSG)
                logging.info(messages.PERIPHERAL_DEVICE_NOT_FOUND_MSG)

            alert_message = (
                f"Please be advised that {device_event_payload.alert_desc} in "
                f"{peripheral_device.location} of {peripheral_device.building.building_name}. "
                f"Please take immediate action to ensure optimal conditions."
            )

            alert_title = device_event_payload.alert_type

            if peripheral_device.business_profile_uuid:
                recipients = await user_service.get_account_users(
                    peripheral_device.business_profile_uuid
                )

                if not recipients:
                    send_client_side_error(
                        messages.DEVICE_ALERT_RECIPIENT_NOT_FOUND_MSG
                    )
                    logging.info(messages.DEVICE_ALERT_RECIPIENT_NOT_FOUND_MSG)

                for recipient in recipients.get("users"):
                    if recipient.get("phone_number") is not None:
                        await send_sms(recipient.get("phone_number"), alert_message)

                    if recipient.get("email_address") is not None:
                        await send_device_alert_email(
                            recipient.get("email_address"),
                            alert_message,
                            alert_title,
                            EmailPurpose.DEVICE_ALERTS,
                        )
            else:
                recipient = await user_service.get_user_by_uuid(
                    peripheral_device.user_uuid
                )

                if not recipient:
                    send_client_side_error(
                        messages.DEVICE_ALERT_RECIPIENT_NOT_FOUND_MSG
                    )
                    logging.info(messages.DEVICE_ALERT_RECIPIENT_NOT_FOUND_MSG)

                await send_sms(recipient.get("phone_number"), alert_message)

        msg = "device event saved"
        return send_info(msg)

    except Exception as e:
        msg = "Failed to process device event"
        logging.error(e)
        return send_internal_server_error(user_msg=msg, error=e)
