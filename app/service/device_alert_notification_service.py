from app.repository.device_alert_notification_repository import (
    DeviceAlertNotificationRepository,
)
from app.service.base_service import BaseService


class DeviceAlertNotificationService(BaseService):
    def __init__(
        self, device_alert_notification_repository: DeviceAlertNotificationRepository
    ):
        self.device_alert_notification_repository = device_alert_notification_repository
        super().__init__(device_alert_notification_repository)

    async def get_recipients_by_node_id(self, node_id: str):
        try:
            devices = (
                await self.device_alert_notification_repository.get_recipients_by_node_id(
                    node_id
                )
            )
            return devices
        except Exception as e:
            raise e
