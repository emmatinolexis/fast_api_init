from app.repository.vehicle_owner_repository import VehicleOwnerRepository
from app.service.base_service import BaseService


class VehicleOwnerService(BaseService):
    def __init__(self, vehicle_owner_repository: VehicleOwnerRepository):
        self.vehicle_owner_repository = vehicle_owner_repository
        super().__init__(vehicle_owner_repository)
