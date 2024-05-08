import uuid

from sqlalchemy import JSON, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class DeviceManufacturer(BaseModel):
    __tablename__ = "device_manufacturers"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    manufacturer_name = Column(
        String(length=50), nullable=False, unique=True, index=True
    )
    shutdown_on_command = Column(JSON, nullable=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)


class Device(BaseModel):
    __tablename__ = "devices"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_inventory_uuid = Column(
        UUID(as_uuid=True), ForeignKey("inventories.uuid"), nullable=True
    )
    device_imei = Column(String(length=100), nullable=True, unique=True, index=True)
    sim_phone_number = Column(
        String(length=100), nullable=True, unique=True, index=True
    )
    assign_to_asset_status = Column(String(length=50), nullable=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    # Relationship to get the associated inventory with device manufacturer
    inventory = relationship("Inventory", backref="device")

    # Relationship to get the associated inventory with device manufacturer
    user = relationship("User", backref="device")

    # Relationship to get the device manufacturer
    manufacturer = relationship(
        "DeviceManufacturer",
        secondary="inventories",
        primaryjoin="Device.device_inventory_uuid == Inventory.uuid",
        secondaryjoin="Inventory.device_manufacturer_uuid == DeviceManufacturer.uuid",
        backref="devices",
        uselist=False,
    )
    asset = relationship(
        "Asset",
        uselist=False,
        primaryjoin="foreign(Device.device_imei) == remote(Asset.device_imei)",
        viewonly=True,
    )
    tracking_events = relationship("TrackingEvent", back_populates="device")
