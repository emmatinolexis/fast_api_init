from app.repository.device_events_repository import DeviceEventRepository
from app.service.base_service import BaseService


class DeviceEventService(BaseService):
    def __init__(self, device_event_repository: DeviceEventRepository):
        self.device_event_repository = device_event_repository
        super().__init__(device_event_repository)

    def get_devices_latest_reading(self, node_id: str):
        try:
            devices = self.device_event_repository.get_device_latest_reading(node_id)
            return devices
        except Exception as e:
            raise e
