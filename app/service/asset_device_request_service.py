from app.core import messages
from app.repository.asset_device_request_repository import AssetDeviceRequestRepository
from app.repository.asset_type_repository import AssetTypeRepository
from app.schema.asset_schema import CreateAssetDeviceRequestPayload, AssetDeviceRequest
from app.service.base_service import BaseService


class AssetDeviceRequestService(BaseService):
    def __init__(
        self,
        asset_device_request_repository: AssetDeviceRequestRepository,
        asset_type_repository: AssetTypeRepository,
    ):
        self.asset_device_request_repository = asset_device_request_repository
        self.asset_type_repository = asset_type_repository
        super().__init__(asset_device_request_repository)

    def get_asset_device_request_by_user_by_asset_type_uuid(
        self, user_uuid: str, asset_type_uuid: str
    ):
        return self.asset_device_request_repository.get_asset_device_request_by_user_by_asset_type_uuid(
            user_uuid, asset_type_uuid
        )

    def create_asset_device_request(self, user_uuid: str, payload: AssetDeviceRequest):
        # check request already exists for the selected asset type
        existing_request = self.get_asset_device_request_by_user_by_asset_type_uuid(
            user_uuid=str(user_uuid),
            asset_type_uuid=str(payload.asset_type_uuid),
        )

        if existing_request:
            raise Exception(messages.ASSET_DEVICE_REQUEST_ALREADY_EXISTS)

        asset_type = self.asset_type_repository.read_by_uuid(
            str(payload.asset_type_uuid)
        )

        if asset_type is None:
            raise Exception(
                messages.ASSET_TYPE_NOT_FOUND + str(payload.asset_type_uuid)
            )

        try:
            payload = CreateAssetDeviceRequestPayload(
                user_uuid=user_uuid,
                asset_type_uuid=payload.asset_type_uuid,
                number_of_assets=payload.number_of_assets,
                metrics=payload.metrics,
            )
            return self.asset_device_request_repository.create(payload)
        except Exception:
            raise Exception(messages.UPDATE_FAILED + " device request")

    def get_asset_device_requests_by_user_uuid(self, user_uuid: str):
        requests = (
            self.asset_device_request_repository.get_asset_device_requests_by_user_uuid(
                user_uuid
            )
        )

        transformed_requests = []

        for request in requests:
            transformed_requests.append(
                {
                    "uuid": request.uuid,
                    "asset_type_uuid": request.asset_type_uuid,
                    "number_of_assets": request.number_of_assets,
                    "metrics": request.metrics,
                    "status": request.status,
                    "created_at": request.created_at,
                    "updated_at": request.updated_at,
                }
            )

        return transformed_requests
