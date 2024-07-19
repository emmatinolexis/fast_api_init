from app.repository.maintenance_alert_repository import MaintenanceAlertRepository
from app.service.base_service import BaseService


class MaintenanceAlertService(BaseService):
    def __init__(self, maintenance_alert_repository: MaintenanceAlertRepository):
        self.maintenance_alert_repository = maintenance_alert_repository
        super().__init__(maintenance_alert_repository)
