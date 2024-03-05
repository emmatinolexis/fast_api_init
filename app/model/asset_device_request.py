import uuid

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.asset_type import AssetType
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
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey(AssetType.uuid), nullable=False, index=True
    )
    number_of_assets = Column(Integer, nullable=False, index=False)
    metrics = Column(ARRAY(String), nullable=False, index=False)
    status = Column(
        String, nullable=False, index=True, default=AssetDeviceRequestStatus.PENDING
    )

    asset_type = relationship("AssetType", back_populates="asset_device_requests")
    user = relationship("User", back_populates="asset_device_requests")
