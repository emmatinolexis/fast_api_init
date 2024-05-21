import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class ThirdPartyApp(BaseModel):
    __tablename__ = "third_party_apps"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    app_name = Column(String(length=50), nullable=False)
    status = Column(Enum(ActiveStatus), default=ActiveStatus.ACTIVE, nullable=False)


class ThirdPartyAppUser(BaseModel):
    __tablename__ = "third_party_app_users"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=50), nullable=False)
    phone_number = Column(String(length=50), nullable=False)
    email = Column(String(length=50), nullable=False)
    password = Column(String(length=100), nullable=False)
    third_party_app_uuid = Column(
        UUID(as_uuid=True), ForeignKey("third_party_apps.uuid"), nullable=False
    )
    status = Column(Enum(ActiveStatus), default=ActiveStatus.ACTIVE, nullable=False)
    third_party_app = relationship("ThirdPartyApp", uselist=False)
