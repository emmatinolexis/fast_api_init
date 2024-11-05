import uuid

from sqlalchemy import Column, Date, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import InstallationStatus


class Installation(BaseModel):
    __tablename__ = "installations"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    id = None
    installed_at = Column(Date, nullable=True)
    assigned_at = Column(Date, nullable=True)
    installer_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.uuid"), nullable=False)
    status = Column(
        Enum(InstallationStatus),
        nullable=False,
        index=True,
        default=InstallationStatus.PENDING_INSTALLATION,
    )
    installer = relationship("User", back_populates="installations")
    order = relationship("Order", back_populates="installations")
