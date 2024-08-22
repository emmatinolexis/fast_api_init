from typing import Optional

from app.repository.building_repository import BuildingRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.asset_schema import (
    BuildingInput,
    CreateBuildingInput,
    GasCylinderPayload,
    UpdateBuildingPayload
)
from app.service.base_service import BaseService
from app.core.exceptions import NotFoundError
from app.core import messages
from app.transfomers.building_transformers import building_transformer


class BuildingService(BaseService):
    def __init__(
        self,
        building_repository: BuildingRepository,
        gas_device_repository: GasDeviceRepository,
        gas_cylinder_repository: GasCylinderRepository,
    ):
        self.building_repository = building_repository
        self.gas_device_repository = gas_device_repository
        self.gas_cylinder_repository = gas_cylinder_repository
        super().__init__(building_repository)

    def create_building(self, payload: BuildingInput):
        try:
            if payload.building:
                # Create new building
                building_data = CreateBuildingInput(
                    building_name=payload.building.building_name,
                    longitude=payload.building.longitude,
                    latitude=payload.building.latitude,
                    image_url=payload.building.image_url,
                    status=payload.building.status,
                    user_uuid=payload.building.user_uuid,
                    business_profile_uuid=payload.building.business_profile_uuid,
                )

                building = self.building_repository.create(building_data)
                building_uuid = building.uuid
            elif payload.building_uuid:
                # Use existing building UUID
                building_uuid = payload.building_uuid
                building = self.building_repository.read_by_uuid(building_uuid)
                if not building:
                    raise ValueError(f"No building found with UUID: {building_uuid}")
            else:
                raise ValueError(
                    "Either 'building' or 'building_uuid' must be provided"
                )

            if payload.create_gas:
                # Create gas cylinder
                cylinder_data = GasCylinderPayload(
                    cylinder_name=payload.gas_cylinder.cylinder_name,
                    material_type=payload.gas_cylinder.material_type,
                    gas_device_serial_number=payload.gas_cylinder.device_serial_number,
                    cylinder_type_uuid=payload.gas_cylinder.cylinder_type_uuid,
                    building_uuid=building_uuid,
                    user_uuid=building.user_uuid,
                    business_profile_uuid=building.business_profile_uuid,
                )

                self.gas_cylinder_repository.create(cylinder_data)

            return building

        except Exception as e:
            if payload.building and "building" in locals():
                self.building_repository.delete_by_uuid(building.uuid)
            raise e

    def get_all_buildings(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        page_size: int = 10,
        page: int = 1,
    ):
        try:
            report = self.building_repository.read_all_building(
                user_uuid=user_uuid,
                business_uuid=business_uuid,
                page=page,
                page_size=page_size,
            )
            return report
        except Exception as e:
            raise e

    def get_building_by_uuid(
        self,
        building_uuid: str = None,
    ):
        try:
            report = self.building_repository.read_building_by_uuid(building_uuid)
            return report
        except Exception as e:
            raise e

    def get_building_cylinder_assets(
        self,
        building_uuid: str,
        cylinder_status: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
    ):
        try:
            cylinders = self.gas_cylinder_repository.get_gas_cylinder_by_building_uuid(
                building_uuid=building_uuid, cylinder_status=cylinder_status
            )

            total = len(cylinders)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_cylinders = cylinders[start_index:end_index]

            return {
                "cylinders": paginated_cylinders,
                "total_cylinders": total,
                "total_pages": (total + page_size - 1) // page_size,
                "current_page": page,
                "page_size": page_size,
            }

        except Exception as e:
            raise e
        

    def update_building(self, building_uuid: str, payload: UpdateBuildingPayload):
        try:
            building = self.building_repository.read_by_uuid(building_uuid)
            if not building:
                raise NotFoundError(messages.BUILDING_NOT_FOUND + building_uuid)

            building = self.building_repository.update_by_uuid(building_uuid,payload)
            return building_transformer(building)
        except Exception as e:
            raise e
