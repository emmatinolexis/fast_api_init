import uuid

from sqlalchemy import FLOAT, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus
from app.model.asset_type import AssetType


class Building(BaseModel):
    __tablename__ = "buildings"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    building_name = Column(String(length=50), nullable=False, index=True)
    longitude = Column(FLOAT, nullable=False, index=True)
    latitude = Column(FLOAT, nullable=False, index=True)
    image_url = Column(String(length=200), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    asset_type_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(AssetType.uuid),
        default="2304facd-4afb-4eff-b28a-6bd5c47e052c",
        nullable=False,
        index=True,
    )
    asset_type = relationship("AssetType", uselist=False)
    gas_cylinders = relationship("GasCylinder", back_populates="building")
    peripheral_devices = relationship("PeripheralDevice", back_populates="building")
