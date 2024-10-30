from typing import List

from app.model.driver_license import DriverLicense
from app.repository.driver_license_repository import DriverLicenseRepository
from app.service.base_service import BaseService


class DriverLicenseService(BaseService):
    def __init__(self, driver_license_repository: DriverLicenseRepository):
        self.driver_license_repository = driver_license_repository
        super().__init__(driver_license_repository)

    def get_all_licenses(self) -> List[DriverLicense]:
        return self.driver_license_repository.get_all_licenses()
