from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.schema.incident_schema import IncidentPayload
from app.service.incident_service import IncidentService
from app.util.utils import send_data, send_data_with_info, send_internal_server_error

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
        return send_data_with_info(data=incident, info=messages.CREATE_SUCCESS)
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
        return send_data(data=incidents)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/location", response_class=ORJSONResponse)
@inject
async def get_incidents_by_location(
    longitude: float,
    latitude: float,
    radius: int = Query(2, description="radius is in kilometers(default is 2km)"),
    service: IncidentService = Depends(Provide[Container.incident_service]),
):
    try:
        incidents = service.get_incidents_by_location(
            longitude=longitude, latitude=latitude, radius=radius * 1000
        )
        return send_data(data=incidents)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)
