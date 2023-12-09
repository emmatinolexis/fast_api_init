import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveInactive


class Feature(BaseModel):
    __tablename__ = "features"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    feature_name = Column(String(length=50), nullable=False, index=True)
    feature_description = Column(String(length=100), nullable=False, index=True)
    icon_url = Column(String(length=100), nullable=False, index=True)
    status = Column(Enum(ActiveInactive), nullable=False, index=True)
