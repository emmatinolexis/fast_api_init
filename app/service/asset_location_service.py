from app.core.exceptions import NotFoundError
from app.repository.asset_location_repository import AssetLocationRepository
from app.repository.asset_repository import AssetRepository
from app.schema.asset_schema import AssetLocationPayload
from app.service.base_service import BaseService


class AssetLocationService(BaseService):
    def __init__(
        self,
        asset_location_repository: AssetLocationRepository,
        asset_repository: AssetRepository,
    ):
        self.asset_location_repository = asset_location_repository
        self.asset_repository = asset_repository
        super().__init__(asset_location_repository)

    def create_asset_location(self, payload: AssetLocationPayload):
        try:
            if self.asset_repository.read_by_uuid(payload.asset_uuid) is None:
                raise NotFoundError(detail=payload.asset_uuid)
            asset_location = self.asset_location_repository.create(payload)
            return asset_location
        except Exception as e:
            raise e

    def update_asset_location(self, uuid: str, payload: AssetLocationPayload):
        try:
            if self.asset_repository.read_by_uuid(payload.asset_uuid) is None:
                raise NotFoundError(detail=payload.asset_uuid)
            asset_location = self.asset_location_repository.update_by_uuid(
                uuid, payload
            )
            return asset_location
        except Exception as e:
            raise e
