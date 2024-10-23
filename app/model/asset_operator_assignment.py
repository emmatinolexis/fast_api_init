from app.model.base_model import BaseModel
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,ForeignKey
from sqlalchemy.orm import relationship




class AssetOperatorAssignment(BaseModel):
    __tablename__ = "asset_operator_assignments"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    operator_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid"),
        nullable=False,
        index=True
    )


    asset_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.uuid"),
        nullable=False,
        index=True,
    )

    operator = relationship("User", foreign_keys=[operator_uuid])
    asset = relationship("Asset", foreign_keys=[asset_uuid])





