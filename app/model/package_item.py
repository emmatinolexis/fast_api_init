import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class PackageItem(BaseModel):
    __tablename__ = "package_items"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    item_name = Column(String(length=50), nullable=False, default="", index=True)
    status = Column(String(length=15), nullable=False, default="", index=True)
