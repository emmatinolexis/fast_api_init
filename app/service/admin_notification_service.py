from app.repository.admin_notification_repository import AdminNotificationRepository
from app.service.base_service import BaseService
from app.core.constants import ADMIN_NOTIFICATION_MAPPING
from app.core.exceptions import UnAuthorizedError
from app.core import messages


class AdminNotificationService(BaseService):
    def __init__(self, admin_notification_repository: AdminNotificationRepository):
        self.admin_notification_repository = admin_notification_repository
        super().__init__(admin_notification_repository)


    
    def get_admin_notifications(self, user_uuid: str, user_role: str):
        try:
            # Check if user role is valid
            if user_role not in ADMIN_NOTIFICATION_MAPPING.keys():
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)
            
            is_super_admin = user_role == "Super Admin"

            # Get notification types for the user's role
            notification_types = ADMIN_NOTIFICATION_MAPPING[user_role]

            # Retrieve notifications from repository
            notifications = self.admin_notification_repository.get_admin_notifications(user_uuid, notification_types,is_super_admin)

            return notifications
        except Exception as e:
            raise e

