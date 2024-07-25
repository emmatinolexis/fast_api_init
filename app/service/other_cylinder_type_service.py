from app.repository.other_cylinder_types_repository import OtherCylinderTypeRepository
from app.service.base_service import BaseService


class OtherCylinderTypeService(BaseService):
    def __init__(self, other_cylinder_type_repository: OtherCylinderTypeRepository):
        self.other_cylinder_type_repository = other_cylinder_type_repository
        super().__init__(other_cylinder_type_repository)
