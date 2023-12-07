import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class EquipmentType(BaseModel):
    __tablename__ = "equipment_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    equipment_type_name = Column(String(length=100), nullable=False, index=True)
    status = Column(String(length=50), nullable=False, index=True)
    equipment_uuid = Column(
        UUID(as_uuid=True), ForeignKey("equipments.uuid"), nullable=True
    )
