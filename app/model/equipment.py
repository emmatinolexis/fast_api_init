import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.asset_type import AssetType
from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class Equipment(BaseModel):
    __tablename__ = "equipments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey(AssetType.uuid), nullable=False
    )
    name = Column(String(length=100), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    marker_icon_url = Column(String(length=100), nullable=False)
    asset_type = relationship("AssetType", uselist=False)
