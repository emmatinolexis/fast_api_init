from app.repository.vehicle_model_repository import VehicleModelRepository
from app.service.base_service import BaseService


class VehicleModelService(BaseService):
    def __init__(self, vehicle_model_repository: VehicleModelRepository):
        self.vehicle_model_repository = vehicle_model_repository
        super().__init__(vehicle_model_repository)
