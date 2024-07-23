from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.service.base_service import BaseService


class GasCylinderService(BaseService):
    def __init__(self, gas_cylinder_repository: GasCylinderRepository):
        self.gas_cylinder_repository = gas_cylinder_repository
        super().__init__(gas_cylinder_repository)

    def unlink_gas_device(self, gas_device_uuid: str):
        return self.gas_cylinder_repository.update_attr_by_uuid(
            gas_device_uuid, "gas_device_uuid", None
        )
