from app.repository.default_device_gateway_configuration_repository import (
    DefaultDeviceGatewayConfigurationRepository
)
from app.service.base_service import BaseService
from app.schema.default_device_gateway_configuration import DefaultDeviceConfiguration


class DefaultDeviceGatewayConfigurationService(BaseService):
    def __init__(
        self, default_device_gateway_configuration_repository: DefaultDeviceGatewayConfigurationRepository
    ):
        self.default_device_gateway_configuration_repository = (
            default_device_gateway_configuration_repository
        )
        super().__init__(default_device_gateway_configuration_repository)

    def create_gateway_configuration(self, default_device_configuration: DefaultDeviceConfiguration):
        data = default_device_configuration.model_dump()
        return self.default_device_gateway_configuration_repository.create_gateway_configuration(data)
