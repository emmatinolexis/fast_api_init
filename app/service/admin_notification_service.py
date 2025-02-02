from app.core import messages
from app.core.constants import ADMIN_NOTIFICATION_MAPPING
from app.core.exceptions import NotFoundError, UnAuthorizedError
from app.repository.admin_notification_repository import AdminNotificationRepository
from app.service.base_service import BaseService


class AdminNotificationService(BaseService):
    def __init__(self, admin_notification_repository: AdminNotificationRepository):
        self.admin_notification_repository = admin_notification_repository
        super().__init__(admin_notification_repository)

    async def get_admin_notifications(self, user_uuid: str, user_role: str):
        try:
            # Check if user role is valid
            if user_role not in ADMIN_NOTIFICATION_MAPPING.keys():
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            is_super_admin = user_role == "Super Admin"

            # Get notification types for the user's role
            notification_types = ADMIN_NOTIFICATION_MAPPING[user_role]

            # Retrieve notifications from repository
            notifications = (
                await self.admin_notification_repository.get_admin_notifications(
                    user_uuid, notification_types, is_super_admin
                )
            )

            return {
                "notifications": notifications,
                "total": len(notifications),
            }
        except Exception as e:
            raise e

    async def read_notification(self, notification_uuid: str, user_uuid: str):
        try:
            # Retrieve notification from repository
            notification = await self.admin_notification_repository.read_by_uuid(
                notification_uuid
            )

            if not notification:
                raise NotFoundError(messages.NOTIFICATION_NOT_FOUND)

            if notification.user_id != user_uuid:
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            # Mark notification as read
            self.admin_notification_repository.read_notification(notification_uuid)

            return notification
        except Exception as e:
            raise e

    async def clear_notifications(self, user_uuid: str):
        try:
            # Clear all notifications
            await self.admin_notification_repository.clear_notifications(user_uuid)

            return messages.NOTIFICATIONS_CLEARED
        except Exception as e:
            raise e
