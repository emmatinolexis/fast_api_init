import uuid

from sqlalchemy import JSON, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel
from app.util.enums import SmartReportStatus


class SmartReport(BaseModel):
    __tablename__ = "smart_reports"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title = Column(String(length=100), nullable=False, unique=True, index=True)
    start_date = Column(String(length=100), nullable=False, index=True)
    end_date = Column(String(length=100), nullable=False, unique=True, index=True)
    asset_group_uuids = Column(JSON, nullable=False)
    report_types = Column(JSON, nullable=False)
    asset_type_uuid = Column(
        UUID(as_uuid=True), ForeignKey("asset_types.uuid"), nullable=False
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    status = Column(Enum(SmartReportStatus), nullable=False, index=True)
    result_url = Column(String(length=200), nullable=True, index=True)
