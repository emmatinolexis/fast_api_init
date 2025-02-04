import uuid
from typing import List, Optional

from app.repository.vehicle_make_repository import VehicleMakeRepository
from app.repository.vehicle_model_repository import VehicleModelRepository
from app.schema.asset_schema import (
    AssetType,
    VehicleMakeInput,
    VehicleMakePayload,
    VehicleMakeResponse,
    VehicleModelInput,
    VehicleModelResponse,
)
from app.service.base_service import BaseService


class VehicleMakeService(BaseService):
    def __init__(
        self,
        vehicle_make_repository: VehicleMakeRepository,
        vehicle_model_repository: VehicleModelRepository,
    ):
        self.vehicle_make_repository = vehicle_make_repository
        self.vehicle_model_repository = vehicle_model_repository
        super().__init__(vehicle_make_repository)

    async def get_vehicle_makes(
        self, asset_type: Optional[AssetType] = None
    ) -> List[VehicleMakeResponse]:
        try:
            makes = await self.vehicle_make_repository.get_vehicle_makes(
                asset_type=asset_type
            )
            return [VehicleMakeResponse.from_orm(make) for make in makes]
        except Exception as e:
            raise e

    async def get_vehicle_models_by_make_uuid(
        self, make_uuid: uuid.UUID
    ) -> List[VehicleModelResponse]:
        try:
            make = await self.vehicle_make_repository.get_vehicle_make_by_uuid(
                make_uuid
            )
            if not make:
                raise ValueError("Vehicle make not found")
            return [VehicleModelResponse.from_orm(model) for model in make.models]
        except Exception as e:
            raise e

    async def create_make(self, payload: VehicleMakePayload):
        try:
            for make in payload.vehicle_makes:
                existing_make = (
                    await self.vehicle_make_repository.get_vehicle_make_name(make.title)
                )

                if existing_make is None:
                    make_data = VehicleMakeInput(
                        name=make.title, asset_type=make.asset_type
                    )
                    created_make = await self.vehicle_make_repository.create(make_data)
                else:
                    created_make = existing_make

                for model in make.models:
                    existing_model = (
                        await self.vehicle_model_repository.get_vehicle_model_name(
                            model.title
                        )
                    )

                    if existing_model is None:
                        model_data = VehicleModelInput(
                            name=model.title,
                            vehicle_make_uuid=created_make.uuid,
                        )
                        await self.vehicle_model_repository.create(model_data)

            return True
        except Exception as e:
            raise e
