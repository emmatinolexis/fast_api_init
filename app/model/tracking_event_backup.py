import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.model.base_model import BaseModel


class TrackingEventBackup(BaseModel):
    __tablename__ = "tracking_event_backups"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    start_date = Column(String(50), index=True, nullable=True)
    end_date = Column(String(50), index=True, nullable=True)
    backup_url = Column(String(200), index=True, nullable=True)
