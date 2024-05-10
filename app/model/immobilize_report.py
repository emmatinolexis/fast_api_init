import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ImmobilizerReason, ImmobilizerType


class ImmobilizerReport(BaseModel):
    __tablename__ = "immobilize_reports"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False, index=True
    )
    asset_uuid = Column(
        UUID(as_uuid=True), ForeignKey("assets.uuid"), nullable=False, index=True
    )
    type = Column(Enum(ImmobilizerType), nullable=False, index=True)
    reason = Column(Enum(ImmobilizerReason), nullable=True, index=True)
    user = relationship("User", uselist=False)
    asset = relationship("Asset", uselist=False)
