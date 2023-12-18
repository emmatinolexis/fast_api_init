import uuid
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from app.core.logger import get_logger

log = get_logger()


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
    log.error(user_msg)
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": user_msg if dev_msg is None else dev_msg,
        },
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
