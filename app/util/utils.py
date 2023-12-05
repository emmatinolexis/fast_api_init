import uuid

from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse


def generate_uuid() -> str:
    return str(uuid.uuid4())


def send_data(data, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "data": jsonable_encoder(data),
        },
    )


def send_message(message: str, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "message": message,
        },
    )
