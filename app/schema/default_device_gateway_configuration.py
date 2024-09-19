from uuid import UUID
from pydantic import BaseModel


class DefaultDeviceConfiguration(BaseModel):
    node_id: str
    update_interval: str
    version: str
    model: str
    mnfdate: str 
    data_url: str
    alert_url: str
    conf_url: str
    ssl_url: str
    wifi_ssid: str
    wifi_password: str
    wifi_static_ip: str
    wifi_gateway: str
    wifi_subnet: str
    hide_wifi: bool