import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class AssetLocation(BaseModel):
    __tablename__ = "asset_locations"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False)
    longitude = Column(String(length=100), nullable=False, index=True)
    latitude = Column(String(length=100), nullable=False, index=True)
