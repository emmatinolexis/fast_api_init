from app.repository.tracking_event_backup_repository import (
    TrackingEventBackupRepository,
)
from app.service.base_service import BaseService


class TrackingEventBackupService(BaseService):
    def __init__(self, tracking_event_backup_repository: TrackingEventBackupRepository):
        self.tracking_event_backup_repository = tracking_event_backup_repository
        super().__init__(tracking_event_backup_repository)

    async def get_backup_by_date_range(self, start_date: str, end_date: str):
        try:
            backup = (
                await self.tracking_event_backup_repository.get_backup_by_date_range(
                    start_date, end_date
                )
            )
            return backup if backup else None
        except Exception as e:
            raise e
