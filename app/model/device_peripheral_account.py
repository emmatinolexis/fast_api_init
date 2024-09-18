import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class DevicePeripheralAccount(BaseModel):
    __tablename__ = "device_peripheral_accounts"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    feature_name = Column(String(length=50), nullable=False, unique=True, index=True)
    feature_description = Column(String(length=100), nullable=False, index=True)
    icon_url = Column(String(length=100), nullable=False, unique=True, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
