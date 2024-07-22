from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.service.base_service import BaseService


class GasCylinderService(BaseService):
    def __init__(self, gas_cylinder_repository: GasCylinderRepository):
        self.gas_cylinder_repository = gas_cylinder_repository
        super().__init__(gas_cylinder_repository)
