from app.repository.notification_repository import NotificationRepository
from app.service.base_service import BaseService


class NotificationService(BaseService):
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
        super().__init__(notification_repository)

    async def get_user_notifications(self, user_uuid: str, is_read: bool = None):
        try:
            notifications = await self.notification_repository.get_user_notifications(
                user_uuid, is_read
            )
            return {"notifications": notifications, "count": len(notifications)}
        except Exception as e:
            raise e

    async def read_notification(self, notification_uuid: str):
        try:
            notification = await self.notification_repository.read_notification(
                notification_uuid
            )
            return notification
        except Exception as e:
            raise e

    async def clear_all_notifications(self, user_uuid: str):
        try:
            await self.notification_repository.clear_all_notifications(user_uuid)
        except Exception as e:
            raise e
