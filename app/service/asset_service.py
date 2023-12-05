import structlog

from app.repository.asset_repository import AssetRepository
from app.repository.driver_repository import DriverRepository
from app.schema.asset_schema import AssetCreate, AssetInput, Driver
from app.service.base_service import BaseService

log = structlog.get_logger()


class AssetService(BaseService):
    def __init__(
        self, asset_repository: AssetRepository, driver_repository: DriverRepository
    ):
        self.asset_repository = asset_repository
        self.driver_repository = driver_repository
        super().__init__(asset_repository)

    def create_asset(self, asset: AssetCreate):
        try:
            created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
            log.info("Asset created", asset=created_asset)
            if asset.add_driver:
                driver_data = Driver(asset_uuid=created_asset.uuid, **asset)
                self.driver_repository.create(driver_data)
                log.info("Driver created", driver=driver_data)
            return created_asset
        except Exception as e:
            raise e
