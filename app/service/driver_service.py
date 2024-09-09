from app.core import messages
from app.core.exceptions import BadRequestError, NotFoundError
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

    def change_rider_asset(self, asset_uuid: str, driver_uuid: str) -> str:
        try:
            # Retrieve the asset and driver from the repository
            asset = self.asset_repository.read_by_uuid(asset_uuid)
            if asset is None:
                raise NotFoundError(messages.ASSET_NOT_FOUND + asset_uuid)

            driver = self.driver_repository.read_by_uuid(driver_uuid)
            if driver is None:
                raise NotFoundError(messages.DRIVER_NOT_FOUND + driver_uuid)

            # Check if the driver is already assigned to the same asset
            if str(driver.asset_uuid) == str(asset_uuid):
                raise BadRequestError(messages.DRIVER_ALREADY_ASSIGNED_SAME_ASSET)

            # Update the old driver's asset UUID to None if it exists
            old_driver = self.driver_repository.get_driver_by_asset_uuid(asset_uuid)
            if old_driver:
                self.driver_repository.update_attr_by_uuid(
                    old_driver.uuid, "asset_uuid", None
                )

            # Update the driver's asset UUID
            self.driver_repository.update_attr_by_uuid(
                driver.uuid, "asset_uuid", asset_uuid
            )

            return messages.UPDATE_SUCCESS + " driver asset"

        except Exception as e:
            # Re-raise the exception to maintain the original error message
            raise e
