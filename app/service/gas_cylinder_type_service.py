from typing import Optional

from app.repository.gas_cylinder_type_repository import GasCylinderTypeRepository
from app.service.base_service import BaseService


class GasCylinderTypeService(BaseService):
    def __init__(self, gas_cylinder_type_repository: GasCylinderTypeRepository):
        self.gas_cylinder_type_repository = gas_cylinder_type_repository
        super().__init__(gas_cylinder_type_repository)

    def filter_by_status_and_name(
        self,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ):
        try:
            return self.gas_cylinder_type_repository.filter_by_status_and_name(
                status=status, search_query=search_query, page=page, page_size=page_size
            )
        except Exception as e:
            raise e
