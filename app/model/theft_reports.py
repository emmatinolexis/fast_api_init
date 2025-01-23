import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class TheftReport(BaseModel):
    __tablename__ = "theft_reports"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    theft_incident_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("theft_incidence.uuid"),
        nullable=False,
        index=True,
    )
    title = Column(String(100), nullable=False)
    report_details = Column(String(200), nullable=False)
