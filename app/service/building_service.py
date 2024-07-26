from app.repository.building_repository import BuildingRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.asset_schema import BuildingInput, CreateBuildingInput, GasCylinderInput
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
            # create building
            building_data = CreateBuildingInput(
                building_name=payload.building_name,
                location=payload.location,
                image_url=payload.image_url,
                status=payload.status,
            )

            building = self.building_repository.create(building_data)

            if building and payload.create_gas:
                # create gas cylinder
                cylinder_data = GasCylinderInput(
                    cylinder_name=payload.gas_cylinder.cylinder_name,
                    material_type=payload.gas_cylinder.material_type,
                    gas_device_serial_number=payload.gas_cylinder.gas_device_serial_no,
                    cylinder_type_uuid=payload.gas_cylinder.cylinder_type_uuid,
                    user_uuid=payload.gas_cylinder.user_uuid,
                    building_uuid=building.uuid,
                    business_profile_uuid=payload.gas_cylinder.business_profile_uuid,
                )
                cylinder = self.gas_cylinder_repository.create(cylinder_data)

                return cylinder
        except Exception as e:
            raise e
