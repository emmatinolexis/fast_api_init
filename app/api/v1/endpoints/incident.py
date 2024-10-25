from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.schema.incident_schema import IncidentPayload
from app.service.incident_service import IncidentService
from app.util.enums import IncidenceType
from app.util.utils import (
    pagination,
    send_data,
    send_data_with_info,
    send_data_with_pagination,
    send_internal_server_error,
    total_pages,
)

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

msg_prefix = "incident"


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_incident(
    payload: IncidentPayload,
    service: IncidentService = Depends(Provide[Container.incident_service]),
):
    try:
        incident = service.create_incident(payload)
        return send_data_with_info(data=incident.dto(), info=messages.CREATE_SUCCESS)
    except Exception as e:
        msg = f"{messages.CREATE_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_incidents(
    incident_type: str = None,
    service: IncidentService = Depends(Provide[Container.incident_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
):
    try:
        incidents = service.get_all_incidents(
            incident_type=incident_type, page_size=page_size, page=page
        )

        incident_count = service.get_all_incidents_count()

        pagination_data = pagination(
            total=incident_count,
            limit=page_size,
            current_page=page,
            total_pages=total_pages(count=incident_count, limit=page_size),
        )

        return send_data_with_pagination(
            data=[i.dto() for i in incidents], pagination=pagination_data
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/location", response_class=ORJSONResponse)
@inject
async def get_incidents_by_location(
    longitude: float,
    latitude: float,
    radius: int = Query(50, description="radius is in meters(default is 50)"),
    service: IncidentService = Depends(Provide[Container.incident_service]),
):
    try:
        incidents = service.get_incidents_by_location(
            longitude=longitude, latitude=latitude, radius=radius
        )
        return send_data(data=[i.dto() for i in incidents])
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/location/incident_type", response_class=ORJSONResponse)
@inject
async def get_incidents_by_incident_type(
    incident_type: IncidenceType,
    longitude: float,
    latitude: float,
    radius: int = Query(50, description="radius is in meters(default is 50)"),
    service: IncidentService = Depends(Provide[Container.incident_service]),
):
    try:
        incidents = service.get_incidents_by_location_incident_type(
            longitude=longitude,
            latitude=latitude,
            radius=radius,
            incident_type=incident_type,
        )
        return send_data(data=[i.dto() for i in incidents])
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/report", response_class=ORJSONResponse)
@inject
async def get_incidents_report(
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: IncidentService = Depends(Provide[Container.incident_service]),
):
    try:
        incidents = service.get_incident_reports(
            start_date=start_date, end_date=end_date, page=page, page_size=page_size
        )
        incident_count = incidents["total"]

        pagination_data = pagination(
            total=incident_count,
            limit=page_size,
            current_page=page,
            total_pages=total_pages(count=incident_count, limit=page_size),
        )

        return send_data_with_pagination(
            data=incidents["data"], pagination=pagination_data
        )

    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}"
        return send_internal_server_error(user_msg=msg, error=e)
