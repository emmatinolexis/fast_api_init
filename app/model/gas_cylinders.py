import uuid

from sqlalchemy import FLOAT, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus, DeviceStatus


class GasDevice(BaseModel):
    __tablename__ = "gas_devices"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_name = Column(String(length=50), nullable=False, unique=True, index=True)
    status = Column(
        Enum(DeviceStatus),
        nullable=False,
        default=DeviceStatus.NOT_ASSIGNED,
        index=True,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=True,
        index=True,
    )


class GasCylinder(BaseModel):
    __tablename__ = "gas_cylinders"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    cylinder_name = Column(String(length=50), nullable=False, unique=True, index=True)
    empty_weight = Column(FLOAT, nullable=False, index=True)
    image_url = Column(String(length=200), nullable=True)
    color = Column(String(length=100), nullable=False, unique=True, index=True)
    status = Column(
        Enum(ActiveStatus), nullable=False, default=ActiveStatus.ACTIVE, index=True
    )
    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False, index=True
    )
    gas_device_uuid = Column(
        UUID(as_uuid=True), ForeignKey("gas_devices.uuid"), nullable=True, index=True
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=True,
        index=True,
    )


class GasCylinderEvent(BaseModel):
    __tablename__ = "gas_cylinder_events"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    gas_device_uuid = Column(
        UUID(as_uuid=True), ForeignKey("gas_devices.uuid"), nullable=False, index=True
    )
    current_weight = Column(FLOAT, nullable=False, index=True)
    battery_level = Column(FLOAT, nullable=True, index=True)
    event_timestamp = Column(DateTime(timezone=True), default=func.now())
