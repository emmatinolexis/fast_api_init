import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import InternalServerError
from app.model.user import User
from app.schema.alert_policy_schema import AlertPolicyType as AlertPolicyTypeSchema
# from app.schema.alert_policy_schema import AlertPolicyTypeFetch
from app.service.alert_policy_type_service import AlertPolicyTypeService
from app.util.utils import send_data, send_message

router = APIRouter(
    prefix="/alert_policy_types",
    tags=["alert policy types"],
)
log = structlog.get_logger()


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_alert_policy_types_handler(
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_list())
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get alert policy types")


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_alert_policy_type_handler(
    alert_policy_type: AlertPolicyTypeSchema,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.add(alert_policy_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not create alert policy type")


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_alert_policy_type_handler(
    uuid: str,
    updated_alert_policy_type: AlertPolicyTypeSchema,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.patch_by_uuid(uuid, updated_alert_policy_type))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not update alert policy type")


@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_alert_policy_types_by_uuid_handler(
    uuid: str,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(service.get_by_uuid(uuid))
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not get alert policy type")


@router.delete("/{uuid}", response_class=ORJSONResponse)
@inject
async def delete_alert_policy_type_by_uuid_handler(
    uuid: str,
    service: AlertPolicyTypeService = Depends(
        Provide[Container.alert_policy_type_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.remove_by_uuid(uuid)
        return send_message("Alert policy type deleted successfully")
    except Exception as e:
        log.error(e)
        raise InternalServerError(detail="Could not delete alert policy type")
