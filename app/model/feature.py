import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class Feature(BaseModel):
    __tablename__ = "features"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    feature_name = Column(String(length=50), nullable=False, default="", index=True)
    feature_description = Column(
        String(length=100), nullable=False, default="", index=True
    )
    icon_url = Column(String(length=100), nullable=False, default="", index=True)
    status = Column(String(length=50), nullable=False, default="", index=True)
