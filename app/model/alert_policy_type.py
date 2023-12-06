import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class AlertPolicyType(BaseModel):
    __tablename__ = "alert_policy_types"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=100), nullable=False, index=True)
    description = Column(String(length=100), nullable=False, index=True)
    status = Column(String(length=100), nullable=False, index=True)
