import uuid

from sqlalchemy import Column, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.model.asset_type import AssetType
from sqlalchemy.orm import relationship


from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class MarkerIcon(BaseModel):
    __tablename__ = "marker_icons"
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
    icon_name = Column(String(length=50), nullable=False, unique=True, index=True)
    icon_url = Column(String(length=100), nullable=False, index=True)
    status = Column(Enum(ActiveStatus), nullable=False, index=True)
    asset_type = relationship("AssetType", uselist=False)

