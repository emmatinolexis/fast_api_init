from app.repository.driver_repository import DriverRepository
from app.service.base_service import BaseService


class DriverService(BaseService):
    def __init__(self, driver_repository: DriverRepository):
        self.driver_repository = driver_repository
        super().__init__(driver_repository)
