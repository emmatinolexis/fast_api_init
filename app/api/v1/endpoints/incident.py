from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.schema.incident_schema import IncidentPayload
from app.service.incident_service import IncidentService
from app.util.utils import send_internal_server_error, send_info, send_data

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
        service.create_incident(payload)
        send_info(messages.CREATE_SUCCESS)
    except Exception as e:
        msg = f"{messages.CREATE_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)
    

@router.get("/",response_class=ORJSONResponse)
@inject
async def get_all_incidents(incident_type:str = None,service: IncidentService = Depends(Provide[Container.incident_service])):
    try:
        incidents = service.get_all_incidents(incident_type=incident_type)
        return send_data(data=incidents)
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix }"
        return send_internal_server_error(user_msg=msg, error=e)
    
                        