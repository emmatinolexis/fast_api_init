from typing import Optional, Union

from pydantic import BaseModel

from app.util.enums import ActiveStatus


class ExternalAppPayload(BaseModel):
    app_id: str
    secret_key: str
    status: ActiveStatus
    no_of_days_to_expire: int

    class Config:
        orm_model = True


class ExternalAppGenerateTokenPayload(BaseModel):
    app_id: str
    secret_key: str
    serial_number: Optional[str] = None
    requires_conf: Optional[bool] = None

    class Config:
        orm_model = True


class AppServiceTokenData(BaseModel):
    secret_key: str = None
    role: Union[str, None] = None
