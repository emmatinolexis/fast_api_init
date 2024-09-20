import uuid

from sqlalchemy import JSON, Column, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import PeripheralDeviceType


class DeviceConfiguration(BaseModel):
    __tablename__ = "device_configurations"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_type = Column(Enum(PeripheralDeviceType), nullable=False, index=True)
    configuration = Column(JSON, nullable=True)
