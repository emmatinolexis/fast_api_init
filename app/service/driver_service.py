from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.driver_repository import DriverRepository
from app.schema.asset_schema import DriverPayload
from app.service.base_service import BaseService


class DriverService(BaseService):
    def __init__(
        self, driver_repository: DriverRepository, asset_repository: AssetRepository
    ):
        self.driver_repository = driver_repository
        self.asset_repository = asset_repository
        super().__init__(driver_repository)

    def create_driver(self, payload: DriverPayload):
        try:
            driver = self.driver_repository.create(payload)
            return driver
        except Exception as e:
            raise e

    def get_drivers_by_user_uuid(self, user_uuid: str, page=1, page_size=10):
        try:
            driver = self.driver_repository.get_drivers_by_user_uuid(
                user_uuid, page, page_size
            )
            return driver
        except Exception as e:
            raise e

    def get_driver_by_phone_number(self, phone_number: str):
        try:
            driver = self.driver_repository.get_driver_phone_number(phone_number)
            return driver
        except Exception as e:
            raise e

    def get_drivers_by_business_uuid(self, business_uuid: str, page=1, page_size=10):
        try:
            driver = self.driver_repository.get_drivers_by_business_uuid(
                business_uuid, page, page_size
            )
            return driver
        except Exception as e:
            raise e

    def update_driver(self, uuid: str, payload: DriverPayload):
        try:
            if self.asset_repository.read_by_uuid(payload.asset_uuid) is None:
                raise NotFoundError(detail=payload.asset_uuid)
            driver = self.driver_repository.update_by_uuid(uuid, payload)
            return driver
        except Exception as e:
            raise e

    def unassign_driver(self, driver_uuid: str):
        try:
            return self.driver_repository.unassign_driver(driver_uuid)
        except Exception as e:
            raise e

    def get_driver_by_uuid(self, uuid: str):
        try:
            driver = self.driver_repository.read_by_uuid(uuid)
            return driver
        except Exception as e:
            raise e
