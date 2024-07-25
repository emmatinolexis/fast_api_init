from app.repository.gas_cylinder_type_repository import GasCylinderTypeRepository
from app.service.base_service import BaseService


class GasCylinderTypeService(BaseService):
    def __init__(self, gas_cylinder_type_repository: GasCylinderTypeRepository):
        self.gas_cylinder_type_repository = gas_cylinder_type_repository
        super().__init__(gas_cylinder_type_repository)
