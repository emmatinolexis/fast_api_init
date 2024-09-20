from app.repository.device_configuration_repository import DeviceConfigurationRepository
from app.schema.peripheral_device_schema import (
    CreateGatewayDeviceConfiguration,
    CreateGatewayDeviceConfigurationInput,
)
from app.service.base_service import BaseService
from app.util.enums import PeripheralDeviceType


class DeviceConfigurationService(BaseService):
    def __init__(self, device_configuration_repository: DeviceConfigurationRepository):
        self.device_configuration_repository = device_configuration_repository
        super().__init__(device_configuration_repository)

    def create_gateway_configuration(self, payload: CreateGatewayDeviceConfiguration):
        try:
            data = CreateGatewayDeviceConfigurationInput(
                device_type=PeripheralDeviceType.GATEWAY_DEVICE,
                configuration={
                    "upload_interval": payload.upload_interval,
                    "version": payload.version,
                    "host_name": payload.host_name,
                    "api_url": payload.api_url,
                    "token_url": payload.token_url,
                    "data_url": payload.data_url,
                    "alert_url": payload.alert_url,
                    "configuration_url": payload.configuration_url,
                    "ssl_url": payload.ssl_url,
                    "wifi_ssid": payload.wifi_ssid,
                    "wifi_password": payload.wifi_password,
                    "wifi_static_ip": payload.wifi_static_ip,
                    "wifi_gateway": payload.wifi_gateway,
                    "wifi_subnet": payload.wifi_subnet,
                    "hide_wifi": payload.hide_wifi,
                },
            )
            conf = self.device_configuration_repository.get_configuration_by_type(
                PeripheralDeviceType.GATEWAY_DEVICE
            )
            if conf is None:
                return self.device_configuration_repository.create(data)
            return self.device_configuration_repository.update_by_uuid(conf.uuid, data)
        except Exception as e:
            raise e
