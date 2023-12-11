from pydantic import BaseModel

from app.util.enums import ActiveStatus


class MarkerIconPayload(BaseModel):
    icon_name: str
    icon_url: str
    status: ActiveStatus
