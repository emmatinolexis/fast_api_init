from app.repository.device_node_configuration_repository import (
    DeviceNodeConfigRepository,
)
from app.service.base_service import BaseService


class DeviceNodeConfigService(BaseService):
    def __init__(self, device_config_repository: DeviceNodeConfigRepository):
        self.device_config_repository = device_config_repository
        super().__init__(device_config_repository)
