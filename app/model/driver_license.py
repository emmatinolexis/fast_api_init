import uuid
from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core import constants
from app.model.base_model import BaseModel


class DriverLicense(BaseModel):
    __tablename__ = "driver_license"
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    license_number = Column(String(length=15), unique=True, index=True, nullable=False)
    expiration_date = Column(Date, nullable=False)
    front_url = Column(String, nullable=False)
    back_url = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User", back_populates="driver_license")

    def is_expired(self):
        return self.expiration_date < datetime.now().date()

    def expires_soon(self):
        return (
            self.expiration_date - datetime.now().date()
        ).days <= constants.EXPIRY_ALERT_PERIOD
