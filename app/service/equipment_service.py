from app.repository.equipment_repository import EquipmentRepository
from app.service.base_service import BaseService


class EquipmentService(BaseService):
    def __init__(self, equipment_repository: EquipmentRepository):
        self.equipment_repository = equipment_repository
        super().__init__(equipment_repository)

    async def get_paginated_equipments(
        self, page=1, page_size=10, search_query=None, status=None
    ):
        try:
            return await self.equipment_repository.get_equipments(
                page=page, page_size=page_size, search_query=search_query, status=status
            )
        except Exception as e:
            raise e
