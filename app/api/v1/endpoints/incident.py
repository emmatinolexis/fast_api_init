from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.schema.incident_schema import IncidentPayload
from app.service.incident_service import IncidentService
from app.util.utils import send_data, send_internal_server_error

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
        send_data(incident)
    except Exception as e:
        msg = f"{messages.CREATE_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)
