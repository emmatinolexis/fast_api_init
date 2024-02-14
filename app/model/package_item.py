import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class PackageItem(BaseModel):
    __tablename__ = "package_items"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    item_name = Column(String(length=50), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    packages = relationship("Package", secondary="package_item_assignments")
