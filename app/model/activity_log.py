import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import ActivityLogClass, ActivityLogType


class ActivityLog(BaseModel):
    __tablename__ = "activity_logs"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    activity_title = Column(String(length=50), nullable=False)
    activity_class = Column(Enum(ActivityLogClass), nullable=False)
    activity_type = Column(Enum(ActivityLogType), nullable=False)
    activity_description = Column(String(length=255), nullable=False)
    ip_address = Column(String(length=50), nullable=False)
