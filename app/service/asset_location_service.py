from app.repository.asset_location_repository import AssetLocationRepository
from app.service.base_service import BaseService


class AssetLocationService(BaseService):
    def __init__(self, asset_location_repository: AssetLocationRepository):
        self.asset_location_repository = asset_location_repository
        super().__init__(asset_location_repository)
