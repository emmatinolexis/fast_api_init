from app.model.user import User
from app.model.installation import Installation
from app.model.order import OrderShippingAddress,Order
from app.events.installation import InstallationCreated
from app.core.database import Database
from app.core.settings import settings
from app.repository.admin_notification_repository import AdminNotificationRepository
from app.schema.notification_schema import CreateNotificationSchema,CreateAdminNotification
from app.core import messages
from app.util.enums import NotificationType


db = Database(settings.DATABASE_URI)

async def create_installation_assigned_notification(event: InstallationCreated):
    user: User = event.user
    installation : Installation = event.installation
    installation_order:Order = installation.order
    installation_location:OrderShippingAddress = installation_order.order_shipping_address


    with db.session() as session:
        # Create NotificationRepository and temporarily override `session_factory`
        notification_repository = AdminNotificationRepository(lambda: session)

        schema = CreateAdminNotification(
            title=messages.DEVICE_INSTALLATION_ASSIGNED,
            message=f"You have been assigned to the installation of order #{installation_order.id} at {installation_location.city}-{installation_location.country} ",
            user_id=str(user.uuid),
            notification_type=NotificationType.INSTALLATION
        )

        # Call `create` without modifying `BaseRepository`
        notification_repository.create(schema=schema)