import uuid

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

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
    device_type = Column(String(50), nullable=False, index=True)
    device_uuid = Column(UUID, nullable=False, index=True)
    device_imei = Column(
        String(15), ForeignKey("devices.device_imei"), nullable=False, index=True
    )
    event_type = Column(String(50), nullable=False, index=True)
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
    device = relationship("Device", back_populates="tracking_events")
    last_checked_geofence_violation = Column(DateTime, default=None, nullable=True)
