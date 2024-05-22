import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class VehicleOwner(BaseModel):
    __tablename__ = "vehicle_owners"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=50), nullable=False, index=True)
    phone_number = Column(String(length=50), nullable=False, unique=True, index=True)
    email_address = Column(String(length=50), nullable=False, unique=True, index=True)
    residential_address = Column(String(length=50), nullable=False, index=True)
