import uuid

from sqlalchemy import JSON, Column, Enum, String,Index
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class DeviceManufacturer(BaseModel):
    __tablename__ = "device_manufacturers"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    manufacturer_name = Column(
        String(length=50), nullable=False, unique=True, index=True
    )
    shutdown_on_command = Column(JSON, nullable=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    __table_args__ = (
        Index('ix_device_manufacturer_name_gin', 'manufacturer_name', postgresql_using='gin'),
    )
