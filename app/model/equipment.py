import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class Equipment(BaseModel):
    __tablename__ = "equipments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=100), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
