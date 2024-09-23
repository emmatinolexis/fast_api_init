import uuid

from sqlalchemy import JSON, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class DeviceConfiguration(BaseModel):
    __tablename__ = "device_configurations"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    configuration_version = Column(
        String(length=100), nullable=False, unique=True, index=True
    )
    configuration = Column(JSON, nullable=True)
