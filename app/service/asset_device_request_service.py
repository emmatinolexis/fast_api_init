from app.core import messages
from app.repository.asset_device_request_repository import AssetDeviceRequestRepository
from app.repository.asset_repository import AssetRepository
from app.schema.asset_schema import AssetDeviceRequest, CreateAssetDeviceRequestPayload
from app.service.base_service import BaseService


class AssetDeviceRequestService(BaseService):
    def __init__(
        self,
        asset_device_request_repository: AssetDeviceRequestRepository,
        asset_repository: AssetRepository,
    ):
        self.asset_device_request_repository = asset_device_request_repository
        self.asset_repository = asset_repository
        super().__init__(asset_device_request_repository)

    def create_asset_device_request(self, user_uuid: str, payload: AssetDeviceRequest):
        assets_to_include_in_request = []

        existing_requests = self.get_asset_device_requests_by_user_uuid(user_uuid)

        for asset_uuid in payload.asset_uuids:
            asset_exists = self.asset_repository.read_by_uuid(str(asset_uuid))

            # check if the request already exists for the selected asset
            asset_exists_in_a_previous_request = any(
                asset_uuid == asset["uuid"]
                for request in existing_requests
                for asset in request["assets"]
            )

            if asset_exists_in_a_previous_request or not asset_exists:
                continue
            else:
                assets_to_include_in_request.append(asset_uuid)

        if not assets_to_include_in_request:
            raise Exception(messages.ASSET_DEVICE_REQUEST_ALREADY_EXISTS)

        payload.asset_uuids = assets_to_include_in_request

        try:
            payload = CreateAssetDeviceRequestPayload(
                user_uuid=user_uuid,
                asset_uuids=payload.asset_uuids,
                metrics=payload.metrics,
            )
            return self.asset_device_request_repository.create_asset_device_request(
                payload
            )
        except Exception:
            raise Exception(messages.CREATE_FAILED + " device request")

    def get_asset_device_requests_by_user_uuid(self, user_uuid: str):
        requests = (
            self.asset_device_request_repository.get_asset_device_requests_by_user_uuid(
                user_uuid
            )
        )

        transformed_requests = []

        for request in requests:
            assets = []

            for asset in request.assets:
                assets.append(
                    {
                        "uuid": asset.uuid,
                        "device_imei": asset.device_imei,
                        "serial_number": asset.serial_number,
                        "vehicle_license_no": asset.vehicle_license_no,
                        "vin": asset.vin,
                        "asset_name": asset.asset_name,
                        "created_at": asset.created_at,
                        "updated_at": asset.updated_at,
                    }
                )
            transformed_requests.append(
                {
                    "uuid": request.uuid,
                    "assets": assets,
                    "metrics": request.metrics,
                    "status": request.status,
                    "created_at": request.created_at,
                    "updated_at": request.updated_at,
                }
            )

        return transformed_requests

    def get_asset_device_requests(self):
        requests = self.asset_device_request_repository.get_asset_device_requests()

        transformed_requests = []

        for request in requests:
            assets = []

            for asset in request.assets:
                assets.append(
                    {
                        "uuid": asset.uuid,
                        "device_imei": asset.device_imei,
                        "serial_number": asset.serial_number,
                        "vehicle_license_no": asset.vehicle_license_no,
                        "vin": asset.vin,
                        "asset_name": asset.asset_name,
                        "created_at": asset.created_at,
                        "updated_at": asset.updated_at,
                    }
                )
            transformed_requests.append(
                {
                    "uuid": request.uuid,
                    "assets": assets,
                    "metrics": request.metrics,
                    "status": request.status,
                    "created_at": request.created_at,
                    "updated_at": request.updated_at,
                }
            )

        return transformed_requests
