import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import Base


class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device_uuid = Column(UUID, nullable=False)
    device_imei = Column(String(15), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_description = Column(String(255))
    event_datetime = Column(DateTime, nullable=False)
    valid = Column(Boolean, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    satellite_quality = Column(Integer)
    hdop = Column(Float)
    speed = Column(Float)
    course = Column(Float)
    altitude = Column(Float)
    milleage = Column(Integer)
    gsm_mcc = Column(Integer)
    gsm_mnc = Column(Integer)
    gsm_lac = Column(String(50))
    gsm_signal_strength = Column(Integer)
    gps_antenna_status = Column(Boolean)
    stop_status = Column(Boolean)
    armed_status = Column(Boolean)
    rfid_login_status = Column(Boolean)
    protocol_version = Column(String(50))
