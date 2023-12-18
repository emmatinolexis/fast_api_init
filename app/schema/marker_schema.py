from pydantic import BaseModel

from app.util.enums import ActiveStatus
from uuid import UUID



class MarkerIconPayload(BaseModel):
    asset_type_uuid: UUID
    icon_name: str
    icon_url: str
    status: ActiveStatus
