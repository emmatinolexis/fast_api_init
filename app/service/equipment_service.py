from app.repository.equipment_repository import EquipmentRepository
from app.service.base_service import BaseService


class EquipmentService(BaseService):
    def __init__(self, equipment_repository: EquipmentRepository):
        self.equipment_repository = equipment_repository
        super().__init__(equipment_repository)

    def get_all_equipments(self):
        return self.equipment_repository.get_all_equipments()
