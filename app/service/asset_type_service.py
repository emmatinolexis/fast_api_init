from app.repository.asset_type_repository import AssetTypeRepository
from app.service.base_service import BaseService


class AssetTypeService(BaseService):
    def __init__(self, asset_type_repository: AssetTypeRepository):
        self.asset_type_repository = asset_type_repository
        super().__init__(asset_type_repository)
