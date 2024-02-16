from app.repository.alert_maintenance_type_repository import (
    AlertMaintenanceTypeRepository,
)
from app.service.base_service import BaseService


class AlertMaintenanceTypeService(BaseService):
    def __init__(
        self, alert_maintenance_type_repository: AlertMaintenanceTypeRepository
    ):
        self.alert_maintenance_type = alert_maintenance_type_repository
        super().__init__(alert_maintenance_type_repository)
