from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus


class EquipmentPayload(BaseModel):
    name: str
    asset_type_uuid: UUID
    status: ActiveStatus
    marker_icon_url: str

    class ConfigDict:
        from_attributes = True


class EquipmentTypePayload(BaseModel):
    equipment_type_name: str
    status: ActiveStatus
    equipment_uuid: Optional[UUID] = None

    class ConfigDict:
        from_attributes = True
