from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.service.base_service import BaseService


class EquipmentTypeService(BaseService):
    def __init__(self, equipment_type_repository: EquipmentTypeRepository):
        self.equipment_type_repository = equipment_type_repository
        super().__init__(equipment_type_repository)
