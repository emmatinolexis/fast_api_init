from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus


class EquipmentPayload(BaseModel):
    name: str
    status: ActiveStatus

    class Config:
        orm_model = True


class EquipmentTypePayload(BaseModel):
    equipment_type_name: str
    status: ActiveStatus
    equipment_uuid: Optional[UUID] = None

    class Config:
        orm_model = True
