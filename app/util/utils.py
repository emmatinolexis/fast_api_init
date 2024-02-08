import uuid
from typing import Any

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE
from app.core.logger import get_logger
from app.core.security import JWTBearer
from app.util.enums import ActiveStatus

log = get_logger()


allow_admins_only = Depends(
    JWTBearer(
        allowed_roles=[
            ADMIN_USER_ROLE,
        ]
    )
)

allow_customers_only = Depends(
    JWTBearer(
        allowed_roles=[
            CUSTOMER_USER_ROLE,
        ]
    )
)

allow_admins_and_customers = Depends(
    JWTBearer(
        allowed_roles=[
            ADMIN_USER_ROLE,
            CUSTOMER_USER_ROLE,
        ]
    )
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def send_data(data: Any, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "data": jsonable_encoder(data),
        },
    )


def send_data_with_info(data: Any, info: str, status_code: int = 200):
    log.info(info)
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
            "data": data,
        },
    )


def send_info(info: str, status_code: int = 200):
    log.info(info)
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
        },
    )


def send_client_side_error(user_msg: str, dev_msg: str = None, status_code: int = 400):
    log.error(user_msg, extra={"error": dev_msg})
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": user_msg if dev_msg is None else dev_msg,
        },
    )


def toggle_status(current_status):
    return (
        ActiveStatus.ACTIVE
        if current_status == ActiveStatus.INACTIVE
        else ActiveStatus.INACTIVE
    )


def send_internal_server_error(user_msg: str, error: Any, status_code: int = 500):
    log.error(user_msg, extra={"error": error})
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": str(error),
        },
    )


def get_status(status: str):
    status_mapping = {
        "Start_Moving": "moving",
        "Stop_Moving": "stopped",
        "Ignition_Off": "stopped",
        "Idling_Alarm": "idle",
        "Time_Interval_Tracking": "moving",
        "Time_Interval_Tracking_Moving": "moving",
        "Time_Interval_Tracking_Stopped": "stopped",
        "Time_Interval_Tracking_Idling": "idle",
    }

    return status_mapping.get(status, "unknown")
