import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.asset_type import AssetType
from app.model.base_model import BaseModel
from app.util.enums import AssetCreators, AssetStatus


class DeviceRequestAssetAssignment(BaseModel):
    __tablename__ = "device_request_asset_assignments"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    device_request_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("asset_device_requests.uuid"),
        nullable=False,
        index=True,
    )

    asset_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.uuid"),
        nullable=False,
        index=True,
    )

    asset_device_request = relationship(
        "AssetDeviceRequest", backref="device_request_asset_assignments"
    )
    asset = relationship("Asset", backref="device_request_asset_assignments")


class Asset(BaseModel):
    __tablename__ = "assets"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_name = Column(String(length=100), nullable=True, index=True)
    asset_status = Column(Enum(AssetStatus), nullable=False, index=True)
    asset_stolen_status = Column(Boolean, nullable=True)
    created_by = Column(Enum(AssetCreators), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    vehicle_license_no = Column(
        String(length=50), nullable=False, unique=True, index=True
    )
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey(AssetType.uuid), nullable=False
    )
    equipment_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("equipment_types.uuid"), nullable=True
    )
    equipment_uuid = Column(
        UUID(as_uuid=True), ForeignKey("equipments.uuid"), nullable=False
    )
    device_imei = Column(
        String(length=100),
        ForeignKey("devices.device_imei"),
        nullable=True,
        index=True,
    )
    vehicle_owner_uuid = Column(
        UUID(as_uuid=True), ForeignKey("vehicle_owners.uuid"), nullable=True
    )
    vin = Column(String(length=100), nullable=True, unique=True, index=True)
    serial_number = Column(String(length=100), nullable=True, unique=True, index=True)
    make = Column(String(length=100), nullable=True, index=True)
    model = Column(String(length=100), nullable=True, index=True)
    marker_icon_uuid = Column(
        UUID(as_uuid=True), ForeignKey("marker_icons.uuid"), nullable=True
    )
    image_url = Column(String(length=200), nullable=True)
    usage_type = Column(String(length=50), nullable=True)
    marker_color = Column(String(length=100), nullable=True, index=True)
    marker_icon = relationship("MarkerIcon", uselist=False)
    user = relationship("User", uselist=False, foreign_keys=[user_uuid])
    asset_type = relationship("AssetType", uselist=False)
    equipment_type = relationship("EquipmentType", uselist=False)
    equipment = relationship("Equipment", uselist=False)
    driver = relationship("Driver", uselist=False, back_populates="asset")
    device = relationship("Device", uselist=False, back_populates="asset")
    device_request = relationship(
        "AssetDeviceRequest", secondary="device_request_asset_assignments"
    )
    vehicle_owner = relationship("VehicleOwner", uselist=False)
    operators = relationship(
        "User", secondary="asset_operator_assignments", back_populates="operated_assets"
    )
