from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.model.user import User
from app.schema.gateway_configuration_schema import GatewayConfigurationSchema
from app.service.gateway_configuration_service import GateWayConfigurationService

from app.schema.default_device_gateway_configuration import DefaultDeviceConfiguration
from app.service.default_device_gateway_configuration_service import DefaultDeviceGatewayConfigurationService


from app.util.utils import (
    send_client_side_error,
    send_data,
    send_internal_server_error,
)
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse


router = APIRouter(
    prefix="/gateway_configuration",
    tags=["gateway_configuration"],
)
msg_prefix = "gateway_configuration"

@router.get("/{uuid}", response_class=ORJSONResponse)
@inject
async def get_configuration_handler(
    uuid: str,
    service: GateWayConfigurationService = Depends(
        Provide[Container.gateway_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        config = service.get_gateway_configuration_by_uuid(uuid)
        return send_data(config)
    except NotFoundError as e:
        msg = str(e)
        return send_client_side_error(user_msg=msg)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_configuration_handler(
    payload: GatewayConfigurationSchema,
    service: GateWayConfigurationService = Depends(
        Provide[Container.gateway_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        config = service.create_gateway_configuration(payload)
        return send_data(config)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_configuration_handler(
    uuid: str,
    payload: GatewayConfigurationSchema,
    service: GateWayConfigurationService = Depends(
        Provide[Container.gateway_configuration_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        config = service.update_gateway_configuration_by_uuid(uuid, payload)
        return send_data(config)
    except NotFoundError as e:
        msg = str(e)
        return send_client_side_error(user_msg=msg)
    except Exception as e:
        msg = messages.UPDATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/create_default_device_gateway_configuration", response_class=ORJSONResponse)
@inject
async def create_default_device_gateway_configuration(
    payload: DefaultDeviceConfiguration,
    service: DefaultDeviceGatewayConfigurationService = Depends(Provide[Container.default_device_gateway_configuration_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        config = service.create_gateway_configuration(payload)
        return send_data(config)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)

