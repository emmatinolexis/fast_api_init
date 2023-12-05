from typing import Optional
from uuid import UUID

from pydantic  import BaseModel


class Equipment(BaseModel):
    name: str
    status: str

    class Config:
        orm_model = True


class EquipmentFetch(BaseModel):
    name: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True


class EquipmentType(BaseModel):
    equipment_type_name: str
    uuid: UUID
    status: str
    equipment_uuid: Optional[UUID] = None
    equipment: Equipment = None

    class Config:
        orm_model = True


class EquipmentTypeCreate(BaseModel):
    equipment_type_name: str
    status: str
    equipment_uuid: Optional[UUID] = None

    class Config:
        orm_model = True
