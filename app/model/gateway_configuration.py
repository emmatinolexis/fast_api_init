import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.model.base_model import BaseModel


class GatewayConfiguration(BaseModel):
    __tablename__ = "gateway_configurations"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    node_id = Column(String(length=100), nullable=False, unique=True, index=True)
    update_interval = Column(
        String(length=100), nullable=False, unique=True, index=True
    )
    version = Column(String(length=100), nullable=False, unique=True, index=True)
    model = Column(String(length=100), nullable=False, unique=True, index=True)
    mnfdate = Column(String(length=100), nullable=False, unique=True, index=True)
    data_url = Column(String(length=100), nullable=False, unique=True, index=True)
    alert_url = Column(String(length=100), nullable=False, unique=True, index=True)
    conf_url = Column(String(length=100), nullable=False, unique=True, index=True)
    ssl_url = Column(String(length=100), nullable=False, unique=True, index=True)
    wifi_ssid = Column(String(length=100), nullable=False, unique=True, index=True)
    wifi_password = Column(String(length=100), nullable=False, unique=True, index=True)
    wifi_static_ip = Column(String(length=100), nullable=False, unique=True, index=True)
    wifi_gateway = Column(String(length=100), nullable=False, unique=True, index=True)
    wifi_subnet = Column(String(length=100), nullable=False, unique=True, index=True)
    hide_wifi = Column(Boolean, nullable=False, index=True)
