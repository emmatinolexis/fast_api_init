from app.core.exceptions import NotFoundError
from app.repository.equipment_repository import EquipmentRepository
from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.schema.equipment_schema import EquipmentTypePayload
from app.service.base_service import BaseService


class EquipmentTypeService(BaseService):
    def __init__(
        self,
        equipment_type_repository: EquipmentTypeRepository,
        equipment_repository: EquipmentRepository,
    ):
        self.equipment_type_repository = equipment_type_repository
        self.equipment_repository = equipment_repository
        super().__init__(equipment_type_repository)

    def create_equipment_type(self, payload: EquipmentTypePayload):
        try:
            if self.equipment_repository.read_by_uuid(payload.equipment_uuid) is None:
                raise NotFoundError(detail=payload.equipment_uuid)
            equipment_type = self.equipment_type_repository.create(payload)
            return equipment_type
        except Exception as e:
            raise e

    def update_equipment_type(self, uuid: str, payload: EquipmentTypePayload):
        try:
            if (
                payload.equipment_uuid is not None
                and self.equipment_repository.read_by_uuid(payload.equipment_uuid)
                is None
            ):
                raise NotFoundError(detail=payload.equipment_uuid)
            equipment_type = self.equipment_type_repository.update_by_uuid(
                uuid, payload
            )
            return equipment_type
        except Exception as e:
            raise e

    def get_equipment_type_by_equipment_uuid(self, equipment_uuid: str) -> None:
        try:
            equipment_types = (
                self.equipment_type_repository.get_equipment_types_by_equipment_uuid(
                    equipment_uuid
                )
            )

            if equipment_types:
                return equipment_types
            else:
                return None
        except Exception as e:
            raise e
