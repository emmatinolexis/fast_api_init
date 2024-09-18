import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import DeviceStatus, DeviceType


class PeripheralDevices(BaseModel):
    __tablename__ = "peripheral_devices"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    serial_number = Column(String(length=50), nullable=False, unique=True, index=True)
    node_id = Column(String(length=50), nullable=False, unique=True, index=True)
    status = Column(
        Enum(DeviceStatus),
        nullable=False,
        default=DeviceStatus.NOT_ASSIGNED,
        index=True,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=True,
        index=True,
    )
    building_uuid = Column(
        UUID(as_uuid=True), ForeignKey("buildings.uuid"), nullable=True, index=True
    )
    location = Column(String(length=50), nullable=True, index=True)
    device_type = Column(Enum(DeviceType), nullable=False, index=True)
    configuration_version = Column(String(length=50), nullable=False, index=True)
