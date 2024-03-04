from app.repository.asset_device_request_repository import AssetDeviceRequestRepository
from app.schema.asset_schema import CreateAssetDeviceRequestPayload
from app.service.base_service import BaseService


class AssetDeviceRequestService(BaseService):
    def __init__(self, asset_device_request_repository: AssetDeviceRequestRepository):
        self.asset_device_request_repository = asset_device_request_repository
        super().__init__(asset_device_request_repository)

    def get_asset_device_request_by_user_by_asset_type_uuid(
        self, user_uuid: str, asset_type_uuid: str
    ):
        return self.asset_device_request_repository.get_asset_device_request_by_user_by_asset_type_uuid(
            user_uuid, asset_type_uuid
        )

    def create_asset_device_request(
        self, asset_device_request: CreateAssetDeviceRequestPayload
    ):
        return self.asset_device_request_repository.create(asset_device_request)
