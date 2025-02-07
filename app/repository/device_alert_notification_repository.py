from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.device_alert_notification import DeviceAlertNotification
from app.repository.base_repository import BaseRepository


class DeviceAlertNotificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceAlertNotification)

    async def get_recipients_by_node_id(self, node_id: str):
        async with self.session_factory() as session:
            stmt = (
                select(self.model)
                .filter(self.model.node_id == str(node_id))
                .options(joinedload(self.model.user))
            )
            result = await session.execute(stmt)
            data = result.unique().scalars().all()

            return [
                {
                    "name": (
                        f"{record.user.first_name} {record.user.last_name}"
                        if record.user
                        else "Unknown"
                    ),
                    "email": record.user.email_address if record.user else None,
                    "phone_number": record.user.phone_number if record.user else None,
                }
                for record in data
            ]
