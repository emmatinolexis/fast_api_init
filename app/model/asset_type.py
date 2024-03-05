import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class AssetType(BaseModel):
    __tablename__ = "asset_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_type_name = Column(String(length=50), nullable=False, unique=True, index=True)
    description = Column(String(length=100), nullable=True, default="", index=True)
    icon_url = Column(String(length=100), nullable=False, default="", index=True)
    status = Column(Enum(ActiveStatus), nullable=False, default="ACTIVE", index=True)

    asset_device_requests = relationship(
        "AssetDeviceRequest", back_populates="asset_type", uselist=True
    )
