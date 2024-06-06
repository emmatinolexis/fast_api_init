from app.repository.alert_policy_type_repository import AlertPolicyTypeRepository
from app.service.base_service import BaseService


class AlertPolicyTypeService(BaseService):
    def __init__(self, alert_policy_type_repository: AlertPolicyTypeRepository):
        self.alert_policy_type_repository = alert_policy_type_repository
        super().__init__(alert_policy_type_repository)
