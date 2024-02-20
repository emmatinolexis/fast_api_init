from app.repository.plan_upgrade_repository import PlanUpgradeRepository
from app.service.base_service import BaseService


class PlanUpgradeService(BaseService):
    def __init__(self, plan_upgrade_repository: PlanUpgradeRepository):
        self.plan_upgrade_repository = plan_upgrade_repository
        super().__init__(plan_upgrade_repository)
