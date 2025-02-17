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

    async def create_equipment_type(self, payload: EquipmentTypePayload):
        try:
            if (
                await self.equipment_repository.read_by_uuid(payload.equipment_uuid)
                is None
            ):
                raise NotFoundError(detail=payload.equipment_uuid)
            equipment_type = await self.equipment_type_repository.create(payload)
            return equipment_type
        except Exception as e:
            raise e

    async def update_equipment_type(self, uuid: str, payload: EquipmentTypePayload):
        try:
            if (
                payload.equipment_uuid is not None
                and await self.equipment_repository.read_by_uuid(payload.equipment_uuid)
                is None
            ):
                raise NotFoundError(detail=payload.equipment_uuid)
            equipment_type = await self.equipment_type_repository.update_by_uuid(
                uuid, payload
            )
            return equipment_type
        except Exception as e:
            raise e

    async def get_equipment_type_by_equipment_uuid(self, equipment_uuid: str) -> None:
        try:
            equipment_types = await self.equipment_type_repository.get_equipment_types_by_equipment_uuid(
                equipment_uuid
            )
            if equipment_types:
                return equipment_types
            else:
                return None
        except Exception as e:
            raise e

    async def get_paginated_equipment_types(
        self, page=1, page_size=10, search_query=None, status=None
    ):
        try:
            return await self.equipment_type_repository.get_equipment_types(
                page=page, page_size=page_size, search_query=search_query, status=status
            )
        except Exception as e:
            raise e
