from app.repository.device_image_repository import DeviceImageRepository
from app.service.base_service import BaseService


class DeviceImageService(BaseService):
    def __init__(self, device_image_repository: DeviceImageRepository):
        self.device_image_repository = device_image_repository
        super().__init__(device_image_repository)
