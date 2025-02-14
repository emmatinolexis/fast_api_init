import uuid

from sqlalchemy import Column, ForeignKey, String, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import AssetType


class VehicleMake(BaseModel):
    __tablename__ = "vehicle_makes"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=50), nullable=False, unique=True, index=True)
    asset_type = Column(String(length=50), nullable=False)
    models = relationship(
        "VehicleModel", back_populates="make", cascade="all, delete-orphan"
    )


class VehicleModel(BaseModel):
    __tablename__ = "vehicle_models"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=50), nullable=False, unique=True, index=True)
    vehicle_make_uuid = Column(
        UUID(as_uuid=True), ForeignKey("vehicle_makes.uuid"), nullable=False
    )
    make = relationship("VehicleMake", back_populates="models")
