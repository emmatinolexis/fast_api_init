from app.events.user import RoleUpdated
from app.model.user import User
from app.model.role import Role
from app.core.database import Database
from app.repository.notification_repository import NotificationRepository
from app.schema.notification_schema import CreateNotificationSchema
from app.core import messages
from app.core.settings import settings

# Instantiate the Database with the correct URI
db = Database(settings.DATABASE_URI)

async def create_role_change_notification(event: RoleUpdated):
    user: User = event.user
    role: Role = event.role

    with db.session() as session:
        # Create NotificationRepository and temporarily override `session_factory`
        notification_repository = NotificationRepository(lambda: session)

        schema = CreateNotificationSchema(
            title=messages.ROLE_UPDATED,
            message=f"Your role has been updated to {role.role_name}",
            user_id=str(user.uuid)
        )

        # Call `create` without modifying `BaseRepository`
        notification_repository.create(schema=schema)

