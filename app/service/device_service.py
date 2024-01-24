from app.repository.device_repository import DeviceRepository
from app.service.base_service import BaseService


class DeviceService(BaseService):
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
        super().__init__(device_repository)
