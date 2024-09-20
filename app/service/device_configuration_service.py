from app.repository.device_configuration_repository import DeviceConfigurationRepository
from app.schema.peripheral_device_schema import (
    CreateDeviceConfigurationInput,
    CreateGatewayDeviceConfiguration,
    CreateNodeConfiguration,
)
from app.service.base_service import BaseService
from app.util.enums import PeripheralDeviceType


class DeviceConfigurationService(BaseService):
    def __init__(self, device_configuration_repository: DeviceConfigurationRepository):
        self.device_configuration_repository = device_configuration_repository
        super().__init__(device_configuration_repository)

    def create_gateway_configuration(self, payload: CreateGatewayDeviceConfiguration):
        try:
            data = CreateDeviceConfigurationInput(
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

    def create_node_configuration(self, payload: CreateNodeConfiguration):
        try:
            data = CreateDeviceConfigurationInput(
                device_type=PeripheralDeviceType.PYROGUARD_NODE_DEVICE,
                configuration={
                    "description": payload.description,
                    "microprocessor_unit": payload.microprocessor_unit,
                    "sensors": payload.sensors,
                    "physical_quantity": payload.physical_quantity,
                    "update_interval": payload.update_interval,
                    "battery_cutoff": payload.battery_cutoff,
                    "observation_time": payload.observation_time,
                    "target_temperature_threshold": payload.target_temperature_threshold,
                    "ambient_temperature_threshold": payload.ambient_temperature_threshold,
                    "humidity_threshold": payload.humidity_threshold,
                    "air_quality_threshold": payload.air_quality_threshold,
                    "critical_mxl_velocity": payload.critical_mxl_velocity,
                    "critical_ambient_temperature": payload.critical_ambient_temperature,
                    "critical_humidity_velocity": payload.critical_humidity_velocity,
                    "critical_air_quality_velocity": payload.critical_air_quality_velocity,
                    "critical_mxl_acceleration": payload.critical_mxl_acceleration,
                    "critical_ambient_temperature_acceleration": payload.critical_ambient_temperature_acceleration,
                    "critical_humidity_acceleration": payload.critical_humidity_acceleration,
                    "critical_air_quality_acceleration": payload.critical_air_quality_acceleration,
                },
            )

            conf = self.device_configuration_repository.get_configuration_by_type(
                PeripheralDeviceType.PYROGUARD_NODE_DEVICE
            )
            if conf is None:
                return self.device_configuration_repository.create(data)
            return self.device_configuration_repository.update_by_uuid(conf.uuid, data)
        except Exception as e:
            raise e

    def get_device_configuration(self):
        try:
            configuration = (
                self.device_configuration_repository.get_configuration_by_type(
                    PeripheralDeviceType.PYROGUARD_NODE_DEVICE
                )
            )
            return configuration
        except Exception as e:
            raise e
