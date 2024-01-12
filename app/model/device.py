import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class Device(BaseModel):
    __tablename__ = "devices"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_name = Column(String(length=50), nullable=False, unique=True, index=True)
    description = Column(String(length=100), nullable=True, index=True)
    device_serial_no = Column(String(length=100), nullable=False, index=True)
    assign_to_asset_status = Column(String(length=50), nullable=False, index=True)
    device_manufacturer_uuid = Column(
        UUID(as_uuid=True), ForeignKey("device_manufacturers.uuid"), nullable=False
    )
    device_manufacturer = relationship("DeviceManufacturer", uselist=False)
