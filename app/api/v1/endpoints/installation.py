from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user_with_permission
from app.model.user import User
from app.schema.asset_schema import AssignDeviceInputPayload
from app.schema.installation_schema import (
    AssignInstallerPayload,
    DeviceConfigurationPayload,
    InstallationPayload,
)
from app.service.asset_service import AssetService
from app.service.installation_service import InstallationService
from app.util.enums import InstallationStatus
from app.util.utils import (
    send_client_side_error,
    send_data,
    send_data_with_info,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/installation",
    tags=["installation"],
)
msg_prefix = "installation"


@router.get("/installers/{installation_uuid}", response_class=ORJSONResponse)
@inject
async def get_installers_handler(
    installation_uuid: str,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(
        get_current_user_with_permission("view_device_installers")
    ),
):
    try:
        installers = service.fetch_all_installers(installation_uuid)
        return send_data(installers)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installers.", error=e
        )


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_installation_handler(
    payload: InstallationPayload,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(
        get_current_user_with_permission("create_device_installation")
    ),
):
    try:
        installation = service.get_installation_by_order_uuid(payload.order_uuid)
        if installation:
            return send_client_side_error(messages.INSTALLATION_CREATED_MSG)

        installation = service.create_installation(payload)
        return send_data(installation)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/assign_installer", response_class=ORJSONResponse)
@inject
async def assign_installer_handler(
    payload: AssignInstallerPayload,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user_with_permission("assign_installer")),
):
    try:
        installation = service.get_installation(payload.installation_uuid)
        if not installation:
            return send_client_side_error(messages.INSTALLATION_NOT_FOUND_MSG)

        installation_to_update = service.assign_installer_to_installation(payload)

        return send_data_with_info(installation_to_update, messages.SUCCESS_MESSAGE)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_installations_handler(
    search_parameter: str = None,
    status: InstallationStatus = None,
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    service: InstallationService = Depends(Provide[Container.installation_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(
        get_current_user_with_permission("view_device_installation")
    ),
):
    try:
        installations = service.fetch_installations(
            page,
            page_size,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search_parameter=search_parameter,
        )
        return send_data(installations)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.get("/installer/installations/{installer_uuid}", response_class=ORJSONResponse)
@inject
async def get_installer_installations_handler(
    installer_uuid: str,
    status: InstallationStatus = None,
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    service: InstallationService = Depends(Provide[Container.installation_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(
        get_current_user_with_permission("view_device_installation")
    ),
):
    try:
        installations = service.fetch_installations(
            page, page_size, installer_uuid, status, start_date, end_date
        )
        return send_data(installations)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.get("/installation/{installation_uuid}", response_class=ORJSONResponse)
@inject
async def get_installation_handler(
    installation_uuid: str,
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(
        get_current_user_with_permission("view_device_installation")
    ),
):
    try:
        installation = service.get_installation(installation_uuid)
        if not installation:
            send_client_side_error(messages.INSTALLATION_NOT_FOUND_MSG)
        return send_data(installation)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.post("/configure", response_class=ORJSONResponse)
@inject
async def configure_device_handler(
    payload: DeviceConfigurationPayload,
    asset_service: AssetService = Depends(Provide[Container.asset_service]),
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(
        get_current_user_with_permission("configure_tracking_device")
    ),
):
    try:
        asset = asset_service.get_assets_by_license_no(payload.asset_license_no)

        if not asset:
            send_client_side_error(
                f"{messages.ASSET_NOT_FOUND} {payload.asset_license_no}"
            )

        data_to_assign = AssignDeviceInputPayload(
            device_imei=payload.device_imei, sim_phone_number=payload.sim_phone_number
        )

        asset_assignment = asset_service.assign_device_imei(asset.uuid, data_to_assign)

        if asset_assignment:
            service.update_installation_status(
                payload.installation_uuid, InstallationStatus.COMPLETED
            )

        return send_data_with_info(asset_assignment, messages.SUCCESS_MESSAGE)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )


@router.get("/towns", response_class=ORJSONResponse)
@inject
async def get_towns_handler(
    service: InstallationService = Depends(Provide[Container.installation_service]),
    current_user: User = Depends(get_current_user_with_permission("configure_tracking_device")),
):
    try:
        towns = service.get_towns()
        return send_data_with_info(towns, messages.SUCCESS_MESSAGE)
    except Exception as e:
        return send_internal_server_error(
            user_msg="Failed to fetch installations.", error=e
        )
