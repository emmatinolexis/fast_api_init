from app.repository.device_manufacturer_repository import \
    DeviceManufacturerRepository
from app.service.base_service import BaseService


class DeviceManufacturerService(BaseService):
    def __init__(self, device_manufacturer_repository: DeviceManufacturerRepository):
        self.device_manufacturer_repository = device_manufacturer_repository
        super().__init__(device_manufacturer_repository)
