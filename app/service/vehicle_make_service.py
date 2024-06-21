from app.repository.vehicle_make_repository import VehicleMakeRepository
from app.repository.vehicle_model_repository import VehicleModelRepository
from app.schema.asset_schema import (VehicleMakeInput, VehicleMakePayload,
                                     VehicleModelInput)
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

    def get_vehicle_makes(self):
        try:
            devices = self.vehicle_make_repository.get_vehicle_makes()
            return devices
        except Exception as e:
            raise e

    def create_makes(self, payload: VehicleMakePayload):
        try:
            for make in payload.vehicle_makes:
                make_to_create = self.vehicle_make_repository.get_vehicle_make_name(
                    make.title
                )
                if make_to_create is None:
                    make_data = VehicleMakeInput(name=make.title)
                    created_make = self.vehicle_make_repository.create(make_data)
                    if created_make:
                        for model in make.models:
                            model_to_create = (
                                self.vehicle_model_repository.get_vehicle_model_name(
                                    model.title
                                )
                            )
                            if model_to_create is None:
                                model_data = VehicleModelInput(
                                    name=model.title,
                                    vehicle_make_uuid=created_make.uuid,
                                )
                                self.vehicle_model_repository.create(model_data)
            return True
        except Exception as e:
            raise e
