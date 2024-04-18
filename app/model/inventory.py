import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import DeviceType


class Inventory(BaseModel):
    __tablename__ = "inventories"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_name = Column(String(length=100), nullable=False, unique=True, index=True)
    device_type = Column(Enum(DeviceType), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, index=True)
    device_manufacturer_uuid = Column(
        UUID(as_uuid=True), ForeignKey("device_manufacturers.uuid"), nullable=False
    )
    cost_price = Column(Integer, nullable=False, index=True)
    selling_price = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=False)
    publish_on_site_status = Column(Boolean, nullable=False)
    manufacturer = relationship("DeviceManufacturer", backref="inventories")
    images = relationship("DeviceImage", backref="inventory")


class DeviceImage(BaseModel):
    __tablename__ = "device_images"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    inventory_uuid = Column(
        UUID(as_uuid=True), ForeignKey("inventories.uuid"), nullable=False
    )
    image_url = Column(String(length=100), nullable=False, index=True)
