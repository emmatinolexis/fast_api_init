import uuid

from sqlalchemy import Column, Enum, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ContactSaleStatus


class ContactSale(BaseModel):
    __tablename__ = "contact_sales"
    id = None
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    phone_number = Column(String(length=30), nullable=True, default="", index=True)
    call_time = Column(Time, nullable=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    status = Column(
        Enum(ContactSaleStatus), nullable=False, default="not_attended", index=True
    )
    user = relationship("User", uselist=False)
