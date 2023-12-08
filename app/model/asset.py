import uuid

from sqlalchemy import Column, ForeignKey, String, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.util.enums import AssetStatus


from app.model.asset_type import AssetType
from app.model.base_model import BaseModel


class Asset(BaseModel):
    __tablename__ = "assets"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_name = Column(String(length=50), nullable=False, index=True)
    asset_status = Column(SQLAlchemyEnum(AssetStatus), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey(AssetType.uuid), nullable=False
    )
    equipment_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("equipment_types.uuid"), nullable=True
    )
    equipment_uuid = Column(
        UUID(as_uuid=True), ForeignKey("equipments.uuid"), nullable=False
    )
    vin = Column(String(length=100), nullable=True, index=True)
    serial_no = Column(String(length=100), nullable=True, index=True)
    make = Column(String(length=100), nullable=True, index=True)
    model = Column(String(length=100), nullable=True, index=True)
    marker_icon_uuid = Column(
        UUID(as_uuid=True), ForeignKey("marker_icons.uuid"), nullable=False
    )
    marker_color = Column(String(length=100), nullable=False, index=True)
    marker_icon = relationship("MarkerIcon", uselist=False)
    user = relationship("User", uselist=False)
    asset_type = relationship("AssetType", uselist=False)
    equipment_type = relationship("EquipmentType", uselist=False)
    equipment = relationship("Equipment", uselist=False)
