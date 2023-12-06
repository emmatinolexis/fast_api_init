import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.alert_policy_schema import AlertPolicy
from app.service.alert_policy_service import AlertPolicyService
from app.util.utils import send_data

router = APIRouter(
    prefix="/alert_policies",
    tags=["alert policies"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_alert_policies_handler(
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_all_alert_policies())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get alert policies")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_policy_handler(
    alert_policy: AlertPolicy,
    service: AlertPolicyService = Depends(Provide[Container.alert_policy_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.create_alert_policy(alert_policy))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create alert policy")
