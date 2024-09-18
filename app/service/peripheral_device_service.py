from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.service.base_service import BaseService


class PeripheralDeviceService(BaseService):
    def __init__(self, peripheral_device_repository: PeripheralDeviceRepository):
        self.peripheral_device_repository = peripheral_device_repository
        super().__init__(peripheral_device_repository)
