import uuid

from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import AssetDeviceRequestStatus


class AssetDeviceRequest(BaseModel):
    __tablename__ = "asset_device_requests"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False, index=True
    )
    metrics = Column(ARRAY(String), nullable=False, index=False)
    status = Column(
        String, nullable=False, index=True, default=AssetDeviceRequestStatus.PENDING
    )

    user = relationship("User", back_populates="asset_device_requests")
    assets = relationship("Asset", secondary="device_request_asset_assignments")
