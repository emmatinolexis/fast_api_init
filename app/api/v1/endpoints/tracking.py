import logging
import socket
import ssl
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_app_service, get_current_user
from app.model.user import User
from app.schema.tracking_device_schema import (
    DeviceConfigurationPayload,
    DeviceReportPayload,
    DeviceReportPayloadInput,
    SSLCertificateRequest,
)
from app.service.asset_service import AssetService
from app.service.device_events_service import DeviceEventService
from app.service.tracking_event_service import TrackingEventService
from app.service.peripheral_device_service import PeripheralDeviceService
from app.util.utils import (
    extract_certificate_info,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
)

from app.util.email import (
    send_alert_policy_violation_email,
    send_maintenance_alert_email,
)

from app.util.sms import send_sms

router = APIRouter(
    prefix="/tracking",
    tags=["device_events"],
)
msg_prefix = "device events"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_last_tracking_details_handler(
    service: TrackingEventService = Depends(Provide[Container.tracking_event_service]),
    current_user: User = Depends(get_current_user),
    device_imei: str = None,
    date: str = None,
):
    try:
        events = service.get_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)
        return send_data(events)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
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
        events = service.get_events_by_user(date=date, user_uuid=user_uuid)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)
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
    date: str = None,
):
    try:
        events = service.get_events_by_user(date=date, business_uuid=business_uuid)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)
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
        events = service.get_route_replay_events_by_device_imei(device_imei, date)
        if events is None:
            return send_client_side_error(user_msg=messages.NO_DATA)
        return send_data(events)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/speed_statistics/{asset_uuid}", response_class=ORJSONResponse)
@inject
async def get_over_speeding_stats_handler(
    asset_uuid: str,
    date_from: datetime,
    date_to: datetime,
    tracking_service: TrackingEventService = Depends(
        Provide[Container.tracking_event_service]
    ),
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        asset = asset_service.get_by_uuid(asset_uuid)

        if asset is None:
            msg = f"{messages.ASSET_NOT_FOUND}{asset_uuid}"
            return send_client_side_error(msg)
        if asset.device_imei is None:
            msg = "Asset not linked to a device"
            return send_client_side_error(msg)
        speeding_data = tracking_service.get_asset_average_speed(
            asset.device_imei, date_from, date_to
        )
        return send_data(speeding_data)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/device_event", response_class=ORJSONResponse)
@inject
async def create_device_events(
    device_event_payload: DeviceReportPayload,
    service: DeviceEventService = Depends(Provide[Container.device_events_service]),
    peripheral_device_service: PeripheralDeviceService = Depends(Provide[Container.peripheral_device_service]),
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

        # Calling the service to add the data
        service.add(data)

        # check if payload.has_alert is true and send email and sms

        # if device_event_payload.has_alert:
        #     peripheral_device = peripheral_device_service.get_device_by_node_id(device_event_payload.node_id)
        #
        #     if peripheral_device:
        #         alert_message = f"This is to inform you that {device_event_payload.alert_desc} in {peripheral_device.location} of {peripheral_device.building.building_name} needs attention. Please take action to maintain optimal conditions."
        #         alert_title = device_event_payload.node_id
        #
        #         await send_sms("+233541557459", alert_message)

        msg = "device event saved"
        logging.info(msg)
        return send_info(msg)

    except Exception as e:
        msg = "Failed to process device event"
        logging.error(msg)
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/certificate/get_ssl_certificate")
@inject
async def get_ssl_certificate(
    request: SSLCertificateRequest,
    current_user: User = Depends(get_current_app_service),
):
    hostname = request.hostname
    port = request.port
    try:
        # Establish a connection to the server
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get the certificate
                cert = ssock.getpeercert()
                extracted_info = extract_certificate_info(cert)
                key = ssl.get_server_certificate((hostname, 443))
                extracted_info["key"] = key

        # Return the certificate information
        return extracted_info

    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        logging.info(msg)
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/create_device_configuration")
@inject
async def create_device_configuration():
    try:
        return "okay"
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        logging.info(msg)
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/get_device_configuration")
@inject
async def get_device_configuration(
    device_type: DeviceConfigurationPayload,
    current_user: User = Depends(get_current_app_service),
):
    try:
        return "okay"
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        logging.info(msg)
        return send_internal_server_error(user_msg=msg, error=e)
