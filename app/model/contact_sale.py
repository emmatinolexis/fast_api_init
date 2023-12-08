import uuid

from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.util.enums import ContactSaleStatus


from app.model.base_model import BaseModel


class ContactSale(BaseModel):
    __tablename__ = "contact_sales"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    phone_number = Column(String(length=20), nullable=True, default="", index=True)
    call_time = Column(String(length=20), nullable=True, default="", index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    status = Column(SQLAlchemyEnum(ContactSaleStatus), nullable=False, default="", index=True)
    user = relationship("User", uselist=False)
