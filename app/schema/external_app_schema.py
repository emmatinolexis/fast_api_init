from pydantic import BaseModel

from app.util.enums import ActiveStatus


class ExternalAppPayload(BaseModel):
    app_id: str
    secret_key: str
    status: ActiveStatus
    no_of_days_to_expire: int

    class Config:
        orm_model = True
