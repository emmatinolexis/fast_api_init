from sqlalchemy import Column, Enum, ForeignKey, String, Text,Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import NotificationType
from uuid import uuid4


class AdminNotifications(BaseModel):
    __tablename__ = "admin_notifications"
    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid4)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)
    is_read = Column(Boolean, default=False)
