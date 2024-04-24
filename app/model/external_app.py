import uuid

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActiveStatus


class ExternalApp(BaseModel):
    __tablename__ = "external_apps"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    app_id = Column(String(length=100), nullable=False, index=True)
    secret_key = Column(String(length=100), nullable=False, index=True)
    no_of_days_to_expire = Column(Integer, nullable=False)
    status = Column(Enum(ActiveStatus), default=ActiveStatus.ACTIVE, nullable=False)
