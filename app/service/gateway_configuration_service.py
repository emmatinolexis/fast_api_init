from app.core.exceptions import NotFoundError
from app.repository.gateway_configuration_repository import (
    GatewayConfigurationRepository,
)
from app.schema.gateway_configuration_schema import GatewayConfigurationSchema
from app.service.base_service import BaseService


class GateWayConfigurationService(BaseService):
    def __init__(
        self, gateway_configuration_repository: GatewayConfigurationRepository
    ):
        super().__init__(gateway_configuration_repository)
        self.gateway_configuration_repository = gateway_configuration_repository

    def get_gateway_configuration_by_uuid(self, uuid: str):
        config = (
            self.gateway_configuration_repository.get_gateway_configuration_by_uuid(
                uuid
            )
        )
        if not config:
            raise NotFoundError("Gateway configuration not found")
        return config

    def create_gateway_configuration(
        self, gateway_configuration: GatewayConfigurationSchema
    ):
        data = gateway_configuration.model_dump()
        return self.gateway_configuration_repository.create_gateway_configuration(data)

    def update_gateway_configuration_by_uuid(
        self, uuid: str, gateway_configuration: GatewayConfigurationSchema
    ):
        data = gateway_configuration.model_dump(exclude_unset=True)
        config = (
            self.gateway_configuration_repository.update_gateway_configuration_by_uuid(
                uuid, data
            )
        )
        if not config:
            raise NotFoundError("Gateway configuration not found")
        return config
