import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.model.base_model import BaseModel


class Settings(BaseModel):
    __tablename__ = "settings"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    primary_colour = Column(String(50), nullable=False)
    secondary_colour = Column(String(50), nullable=True)
    button_colour = Column(String(50), nullable=True)
    logo_url = Column(String(200), nullable=False)
