from app.repository.device_events_repository import DeviceEventRepository
from app.service.base_service import BaseService


class DeviceEventService(BaseService):
    def __init__(self, device_event_repository: DeviceEventRepository):
        self.device_event_repository = device_event_repository
        super().__init__(device_event_repository)
