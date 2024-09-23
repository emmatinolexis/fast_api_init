from app.repository.device_configuration_repository import DeviceConfigurationRepository
from app.schema.peripheral_device_schema import (
    CreateDeviceConfigurationInput,
    CreateGatewayDeviceConfiguration,
    CreateNodeConfiguration,
)
from app.service.base_service import BaseService
from app.util.enums import DeviceConfigurationVersion


class DeviceConfigurationService(BaseService):
    def __init__(self, device_configuration_repository: DeviceConfigurationRepository):
        self.device_configuration_repository = device_configuration_repository
        super().__init__(device_configuration_repository)

    def create_gateway_configuration(self, payload: CreateGatewayDeviceConfiguration):
        try:
            data = CreateDeviceConfigurationInput(
                configuration_version=payload.configuration_version,
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
                payload.configuration_version
            )
            if conf is None:
                return self.device_configuration_repository.create(data)
            return self.device_configuration_repository.update_by_uuid(conf.uuid, data)
        except Exception as e:
            raise e

    def create_node_configuration(self, payload: CreateNodeConfiguration):
        try:
            if (
                payload.configuration_version
                == DeviceConfigurationVersion.SG_PYROGAURDE_V1
            ):
                data = CreateDeviceConfigurationInput(
                    configuration_version=payload.configuration_version,
                    configuration={
                        "description": payload.description,
                        "microprocessor_unit": payload.microprocessor_unit,
                        "sensors": payload.sensors,
                        "physical_quantity": payload.physical_quantity,
                        "update_interval": payload.update_interval,
                        "battery_cutoff": payload.battery_cutoff,
                        "observation_time": payload.observation_time,
                        "target_temperature_threshold": payload.pyro_node_configuration.get(
                            "target_temperature_threshold"
                        ),
                        "ambient_temperature_threshold": payload.pyro_node_configuration.get(
                            "ambient_temperature_threshold"
                        ),
                        "humidity_threshold": payload.pyro_node_configuration.get(
                            "humidity_threshold"
                        ),
                        "air_quality_threshold": payload.pyro_node_configuration.get(
                            "air_quality_threshold"
                        ),
                        "critical_mxl_velocity": payload.pyro_node_configuration.get(
                            "critical_mxl_velocity"
                        ),
                        "critical_ambient_temperature": payload.pyro_node_configuration.get(
                            "critical_ambient_temperature"
                        ),
                        "critical_humidity_velocity": payload.pyro_node_configuration.get(
                            "critical_humidity_velocity"
                        ),
                        "critical_air_quality_velocity": payload.pyro_node_configuration.get(
                            "critical_air_quality_velocity"
                        ),
                        "critical_mxl_acceleration": payload.pyro_node_configuration.get(
                            "critical_mxl_acceleration"
                        ),
                        "critical_ambient_temperature_acceleration": payload.pyro_node_configuration.get(
                            "critical_ambient_temperature_acceleration"
                        ),
                        "critical_humidity_acceleration": payload.pyro_node_configuration.get(
                            "critical_humidity_acceleration"
                        ),
                        "critical_air_quality_acceleration": payload.pyro_node_configuration.get(
                            "critical_air_quality_acceleration"
                        ),
                    },
                )

            if (
                payload.configuration_version
                == DeviceConfigurationVersion.SG_GGAURGEPRO_VI
            ):
                data = CreateDeviceConfigurationInput(
                    configuration_version=payload.configuration_version,
                    configuration={
                        "description": payload.description,
                        "microprocessor_unit": payload.microprocessor_unit,
                        "sensors": payload.sensors,
                        "physical_quantity": payload.physical_quantity,
                        "update_interval": payload.update_interval,
                        "battery_cutoff": payload.battery_cutoff,
                        "observation_time": payload.observation_time,
                        "threshold_1": payload.gas_node_configuration.threshold_1,
                        "threshold_2": payload.gas_node_configuration.threshold_2,
                        "threshold_3": payload.gas_node_configuration.threshold_3,
                    },
                )

            conf = self.device_configuration_repository.get_configuration_by_type(
                payload.configuration_version
            )
            if conf is None:
                return self.device_configuration_repository.create(data)
            return self.device_configuration_repository.update_by_uuid(conf.uuid, data)
        except Exception as e:
            raise e

    def get_device_configuration(
        self, configuration_version: DeviceConfigurationVersion
    ):
        try:
            configuration = (
                self.device_configuration_repository.get_configuration_by_type(
                    configuration_version
                )
            )
            return configuration
        except Exception as e:
            raise e
