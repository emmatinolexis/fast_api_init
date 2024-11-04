from app.events.user import RoleUpdated,VehicleAssignment,VehicleUnassignment
from app.model.user import User
from app.model.role import Role
from app.model.asset import Asset
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



async def asset_change_notification(event: VehicleAssignment):
    user: User = event.user
    asset: Asset = event.asset

    with db.session() as session:
        # Create NotificationRepository and temporarily override `session_factory`
        notification_repository = NotificationRepository(lambda: session)

        schema = CreateNotificationSchema(
            title=messages.ASSIGNMENT_SUCCESS,
            message=f"You have been assigned to {asset.asset_name} with license plate {asset.vehicle_license_no}",
            user_id=str(user.uuid)  # Convert user.uuid to string
        )

        # Call `create` without modifying `BaseRepository`
        notification_repository.create(schema=schema)



async def asset_removal_notification(event: VehicleUnassignment):
    user: User = event.user
    asset: Asset = event.asset

    with db.session() as session:
        # Create NotificationRepository and temporarily override `session_factory`
        notification_repository = NotificationRepository(lambda: session)

        schema = CreateNotificationSchema(
            title=messages.REMOVAL_SUCCESS,
            message=f"You have been removed from {asset.asset_name} with license plate {asset.vehicle_license_no}",
            user_id=str(user.uuid)  # Convert user.uuid to string
        )

        # Call `create` without modifying `BaseRepository`
        notification_repository.create(schema=schema)


