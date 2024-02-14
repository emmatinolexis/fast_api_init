import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class PackageItemAssignment(BaseModel):
    __tablename__ = "package_item_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    package_uuid = Column(
        UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=False
    )
    package_item_uuid = Column(
        UUID(as_uuid=True), ForeignKey("package_items.uuid"), nullable=False
    )
    package = relationship("Package", backref="package_item_assignments")
    package_item = relationship("PackageItem", backref="package_item_assignments")
