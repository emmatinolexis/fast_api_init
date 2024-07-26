from app.repository.building_repository import BuildingRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.asset_schema import (
    BuildingInput,
    CreateBuildingInput,
    GasCylinderPayload,
)
from app.service.base_service import BaseService


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
            # Create building
            building_data = CreateBuildingInput(
                building_name=payload.building.building_name,
                location=payload.building.location,
                image_url=payload.building.image_url,
                status=payload.building.status,
                user_uuid=payload.building.user_uuid,
                business_profile_uuid=payload.building.business_profile_uuid,
            )

            building = self.building_repository.create(building_data)

            if building and payload.create_gas:
                try:
                    # Create gas cylinder
                    cylinder_data = GasCylinderPayload(
                        cylinder_name=payload.gas_cylinder.cylinder_name,
                        material_type=payload.gas_cylinder.material_type,
                        device_serial_number=payload.gas_cylinder.device_serial_number,
                        cylinder_type_uuid=payload.gas_cylinder.cylinder_type_uuid,
                        building_uuid=building.uuid,
                        user_uuid=payload.building.user_uuid,
                        business_profile_uuid=payload.building.business_profile_uuid,
                    )

                    self.gas_cylinder_repository.create(cylinder_data)
                    return building
                except Exception as e:
                    self.building_repository.delete_by_uuid(building.uuid)
                    raise e
        except Exception as e:
            raise e
