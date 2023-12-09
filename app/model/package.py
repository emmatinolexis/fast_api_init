import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.model.package_item_assignment import PackageItemAssignment


class Package(BaseModel):
    __tablename__ = "packages"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    package_name = Column(String(length=50), nullable=False, default="", index=True)
    package_price = Column(String(length=50), nullable=False, default="", index=True)
    package_description = Column(
        String(length=100), nullable=True, default="", index=True
    )
    package_item_assignments = relationship(PackageItemAssignment, uselist=True)
