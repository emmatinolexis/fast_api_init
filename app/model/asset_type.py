import uuid

from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from app.util.enums import ActiveInactive

from app.model.base_model import BaseModel


class AssetType(BaseModel):
    __tablename__ = "asset_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_type_name = Column(String(length=50), nullable=False, default="", index=True)
    description = Column(String(length=100), nullable=True, default="", index=True)
    icon_url = Column(String(length=100), nullable=False, default="", index=True)
    status = Column(SQLAlchemyEnum(ActiveInactive), nullable=False, default="", index=True)
