import uuid

from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from app.util.enums import ActiveInactive


from app.model.base_model import BaseModel


class MarkerIcon(BaseModel):
    __tablename__ = "marker_icons"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    icon_name = Column(String(length=50), nullable=False, index=True)
    icon_url = Column(String(length=100), nullable=False, index=True)
    status = Column(SQLAlchemyEnum(ActiveInactive), nullable=False, index=True)
