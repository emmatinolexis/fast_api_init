from app.repository.gas_device_repository import GasDeviceRepository
from app.service.base_service import BaseService


class GasDeviceService(BaseService):
    def __init__(self, gas_device_repository: GasDeviceRepository):
        self.gas_device_repository = gas_device_repository
        super().__init__(gas_device_repository)
