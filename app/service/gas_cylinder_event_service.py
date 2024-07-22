from app.repository.gas_cylinder_event_repository import GasCylinderEventRepository
from app.service.base_service import BaseService


class GasCylinderEventService(BaseService):
    def __init__(self, gas_cylinder_event_repository: GasCylinderEventRepository):
        self.gas_cylinder_event_repository = gas_cylinder_event_repository
        super().__init__(gas_cylinder_event_repository)
