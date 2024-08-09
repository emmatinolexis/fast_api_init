import uuid

from sqlalchemy import FLOAT, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class FuelLog(BaseModel):
    __tablename__ = "fuel_logs"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    amount = Column(FLOAT, nullable=False, index=True)
    quantity = Column(FLOAT, nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    asset_uuid = Column(UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=True)
    asset_name = Column(String(length=100), nullable=True)
    driver_name = Column(String(length=100), nullable=True)
    receipt_image = Column(String(length=255), nullable=True)
    purchase_date = Column(String(length=100), nullable=True)
