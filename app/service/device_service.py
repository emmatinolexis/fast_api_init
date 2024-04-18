from app.repository.device_repository import DeviceRepository
from app.service.base_service import BaseService


class DeviceService(BaseService):
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
        super().__init__(device_repository)

    def get_devices_by_user_uuid(self, user_uuid: str):
        try:
            devices = self.device_repository.get_devices_by_user_uuid(user_uuid)
            return devices
        except Exception as e:
            raise e

    def get_all_devices(self):
        try:
            devices = self.device_repository.get_all_devices()
            return devices
        except Exception as e:
            raise e
