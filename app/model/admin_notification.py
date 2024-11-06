from app.model.base_model import BaseModel
from sqlalchemy import Column,String,Text,Integer,ForeignKey,Enum
from sqlalchemy.dialects.postgresql import UUID
from app.util.enums import NotificationType





class AdminNotifications(BaseModel):
    __tablename__ = 'admin_notifications'
    title = Column(String(255),nullable=False)
    message = Column(Text,nullable=False)
    notification_type = Column(Enum(NotificationType),nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)

    




