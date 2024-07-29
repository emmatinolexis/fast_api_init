import uuid

from sqlalchemy import FLOAT, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus, DeviceStatus, GasCylinderMaterialType


class GasCylinder(BaseModel):
    __tablename__ = "gas_cylinders"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    cylinder_name = Column(String(length=50), nullable=False, index=True)
    status = Column(
        Enum(ActiveStatus), nullable=False, default=ActiveStatus.ACTIVE, index=True
    )
    material_type = Column(Enum(GasCylinderMaterialType), nullable=False, index=True)
    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False, index=True
    )
    building_uuid = Column(
        UUID(as_uuid=True), ForeignKey("buildings.uuid"), nullable=False, index=True
    )
    gas_device_serial_number = Column(
        String(length=50),
        ForeignKey("gas_devices.serial_number"),
        nullable=True,
        index=True,
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.uuid"),
        nullable=True,
        index=True,
    )
    cylinder_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("cylinder_types.uuid"), nullable=True, index=True
    )

    other_cylinder_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("cylinder_types.uuid"), nullable=True, index=True
    )
    building = relationship("Building", back_populates="gas_cylinders")
    gas_events = relationship(
        "GasCylinderEvent",
        primaryjoin="GasCylinder.gas_device_serial_number == foreign(GasCylinderEvent.device_serial_number)",
        # back_populates="gas_cylinder",
    )
    gas_device = relationship(
        "GasDevice",
        primaryjoin="GasCylinder.gas_device_serial_number == foreign(GasDevice.serial_number)",
        # back_populates="cylinders",
        uselist=False,
    )

    cylinder_type = relationship(
        "CylinderTypes",
        primaryjoin="GasCylinder.cylinder_type_uuid == foreign(CylinderTypes.uuid)",
        uselist=False,
        # back_populates="gas_cylinders",
    )


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
    serial_number = Column(String(length=50), nullable=False, unique=True, index=True)
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
    # cylinders = relationship(
    #     "GasCylinder",
    #     primaryjoin="GasDevice.serial_number == foreign(GasCylinder.device_serial_number)",
    #     back_populates="gas_device",
    # )


class CylinderTypes(BaseModel):
    __tablename__ = "cylinder_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=50), nullable=False, unique=True, index=True)
    empty_weight = Column(FLOAT, nullable=False, index=True)
    full_weight = Column(FLOAT, nullable=False, index=True)
    status = Column(
        Enum(ActiveStatus), nullable=False, default=ActiveStatus.ACTIVE, index=True
    )
    # gas_cylinders = relationship(
    #     "GasCylinder",
    #     primaryjoin="CylinderTypes.uuid == foreign(GasCylinder.cylinder_type_uuid)",
    #     back_populates="cylinder_type",
    # )


class OtherCylinderTypes(BaseModel):
    __tablename__ = "other_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=50), nullable=False, unique=True, index=True)
    image_url = Column(String(length=200), nullable=True)
    empty_weight = Column(FLOAT, nullable=False, index=True)
    full_weight = Column(FLOAT, nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
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
    device_serial_number = Column(
        String(length=50),
        nullable=False,
        index=True,
    )
    current_weight = Column(FLOAT, nullable=False, index=True)
    battery_level = Column(FLOAT, nullable=True, index=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=True)
    # gas_cylinder = relationship(
    #     "GasCylinder",
    #     primaryjoin="GasCylinderEvent.device_serial_number == foreign(GasCylinder.device_serial_number)",
    #     back_populates="gas_events",
    #     uselist=False
    # )
